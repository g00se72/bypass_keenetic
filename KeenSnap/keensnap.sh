#!/bin/sh

for arg in "$@"; do
    case "$arg" in
        LOG_FILE=*) LOG_FILE="${arg#*=}" ;;
        SELECTED_DRIVE=*) SELECTED_DRIVE="${arg#*=}" ;;
        BACKUP_STARTUP_CONFIG=*) BACKUP_STARTUP_CONFIG="${arg#*=}" ;;
        BACKUP_FIRMWARE=*) BACKUP_FIRMWARE="${arg#*=}" ;;
        BACKUP_ENTWARE=*) BACKUP_ENTWARE="${arg#*=}" ;;
        BACKUP_CUSTOM_FILES=*) BACKUP_CUSTOM_FILES="${arg#*=}" ;;
        CUSTOM_BACKUP_PATHS=*) CUSTOM_BACKUP_PATHS="${arg#*=}" ;;
    esac
done

date="backup$(date +%Y-%m-%d_%H-%M)"

progress() {
    echo "{\"type\": \"progress\", \"message\": \"$*\"}"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >> "$LOG_FILE"
}

clean_log() {
    local log_file="$1"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
        return
    fi
	
    local file_size=$(wc -c < "$log_file")
    local max_size=524288
    if [ "$file_size" -gt "$max_size" ]; then
        tail -n 50 "$log_file" >"$log_file.tmp" && mv "$log_file.tmp" "$log_file"
    fi
}

get_device_info() {
    version_output=$(ndmc -c show version 2>/dev/null)
    DEVICE=$(echo "$version_output" | grep "device:" | awk -F": " '{print $2}')
    RELEASE=$(echo "$version_output" | grep "release:" | awk -F": " '{print $2}')
    SANDBOX=$(echo "$version_output" | grep "sandbox:" | awk -F": " '{print $2}')
    DEVICE_ID=$(echo "$version_output" | grep "hw_id:" | awk -F": " '{print $2}')

    [ -z "$DEVICE" ] && DEVICE="unknown"
    [ -z "$RELEASE" ] && RELEASE="unknown"
    [ -z "$SANDBOX" ] && SANDBOX="unknown"
    [ -z "$DEVICE_ID" ] && DEVICE_ID="unknown"

    FW_VERSION="${SANDBOX}_${RELEASE}"
}

get_architecture() {
    arch=$(opkg print-architecture | grep -oE 'mips-3|mipsel-3|aarch64-3|armv7' | head -n 1)
    case "$arch" in
        "mips-3") echo "mips" ;;
        "mipsel-3") echo "mipsel" ;;
        "aarch64-3") echo "aarch64" ;;
        "armv7") echo "armv7" ;;
        *) echo "unknown_arch" ;;
    esac
}

check_free_space() {
    local source_size_kb="$1"
    local backup_name="$2"
    local multiplier="$3"
    local required_size_kb=$((source_size_kb * multiplier))
    local available_size_kb=$(df -k "$SELECTED_DRIVE" | tail -n 1 | awk '{print $4}')
    if [ "$available_size_kb" -lt "$required_size_kb" ]; then
        error "Недостаточно места для $backup_name (нужно $((required_size_kb / 1024)) MB, доступно $((available_size_kb / 1024)) MB)"
        return 1
    fi
    progress "Для $backup_name (нужно $((required_size_kb / 1024)) MB, доступно $((available_size_kb / 1024)) MB)"
    return 0
}

backup_startup_config() {
    local item_name="startup-config"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.txt"
    progress "Создаю бэкап $item_name в $backup_file"
	
    if ! ndmc -c "copy $item_name $backup_file" >/dev/null 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    return 0
}

backup_firmware() {
    local item_name="firmware"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.bin"
    local source_size_kb=20480
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап $item_name в $backup_file"

    if ! ndmc -c "copy flash:/$item_name $backup_file" >/dev/null 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    return 0
}

backup_entware() {
    local item_name="Entware"
    local backup_file="$SELECTED_DRIVE/$date/$(get_architecture)-installer.tar.gz"
    local source_size_kb=$(du -s /opt | awk '{print $1}')
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап $item_name в $backup_file"
    local exclude_file=$(mktemp)
    echo "$backup_file" > "$exclude_file"
    if ! tar czf "$backup_file" -X "$exclude_file" -C /opt . 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    rm -f "$exclude_file"
    return 0
}

backup_custom_files() {
    local item_name="custom-files"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    
    if [ -z "$CUSTOM_BACKUP_PATHS" ]; then
        error "Переменная CUSTOM_BACKUP_PATHS не задана в bot_config.py"
        return 1
    fi

    local source_size_kb=0
	
    for path in $CUSTOM_BACKUP_PATHS; do
        if [ -e "$path" ]; then
            local path_size_kb=$(du -s "$path" | awk '{print $1}')
            source_size_kb=$((source_size_kb + path_size_kb))
        fi
    done
    
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап: $CUSTOM_BACKUP_PATHS в $folder_pah"
    
    for path in $CUSTOM_BACKUP_PATHS; do
        if ! cp -r "$path" "$SELECTED_DRIVE/$date/" 2>>"$LOG_FILE"; then
            error "Ошибка при копировании $path"
            return 1
        fi
    done
    return 0
}

create_backup() {
    if [ -z "$SELECTED_DRIVE" ]; then
        echo "{\"status\": \"error\", \"message\": \"Не указан путь к диску для бэкапа\"}"
        return 1
    fi

    if [ ! -d "$SELECTED_DRIVE" ]; then
        echo "{\"status\": \"error\", \"message\": \"Указанный путь недоступен: $SELECTED_DRIVE\"}"
        return 1
    fi

    progress "Выбран диск: $SELECTED_DRIVE"
    progress "Создаю временную папку: $SELECTED_DRIVE/$date"
    mkdir -p "$SELECTED_DRIVE/$date"
    local backup_performed=0
    local backup_failed=0

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files && backup_performed=1 || backup_failed=1; }

    if [ "$backup_failed" -eq 1 ]; then
        error "Один или несколько бэкапов завершились с ошибкой"
        echo "{\"status\": \"error\", \"message\": \"Один или несколько бэкапов завершились с ошибкой, см. $LOG_FILE\"}"
        rm -rf "$SELECTED_DRIVE/$date"
        return 1
    fi

    progress "Все бэкапы завершены"
    local total_size_kb=$(du -s "$SELECTED_DRIVE/$date" | awk '{print $1}')
    check_free_space "$total_size_kb" "финального архива" 2 || { 
        rm -rf "$SELECTED_DRIVE/$date"
        echo "{\"status\": \"error\", \"message\": \"Недостаточно места для финального архива, см. $LOG_FILE\"}"
        return 1
    }
    local archive_path="$SELECTED_DRIVE/${DEVICE_ID}_$date.tar.gz"
    progress "Создаю финальный архив в $archive_path"
	
    if tar -czf "$archive_path" -C "$SELECTED_DRIVE" "$date" 2>>"$LOG_FILE"; then
        progress "Архив успешно создан: $archive_path"
        echo "{\"status\": \"success\", \"archive_path\": \"$archive_path\"}"
    else
        error "Ошибка при создании архива"
        echo "{\"status\": \"error\", \"message\": \"Ошибка при создании финального архива\"}"
        rm -rf "$SELECTED_DRIVE/$date"
        return 1
    fi
    progress "Удаляю временную папку $SELECTED_DRIVE/$date"
    rm -rf "$SELECTED_DRIVE/$date"
}

main() {
    clean_log "$LOG_FILE"
    get_device_info
    create_backup
}

main
