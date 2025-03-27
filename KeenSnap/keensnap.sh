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

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >> "$LOG_FILE"
}

clean_log() {
    local log_file="$1"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
    tail -n 50 "$log_file" >"$log_file.tmp" && mv "$log_file.tmp" "$log_file"
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
    return 0
}

backup_startup_config() {
    local item_name="startup-config"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.txt"
    ndmc -c "copy $item_name $backup_file" >/dev/null 2>&1 || error "Ошибка при сохранении $item_name"
}

backup_entware() {
    local item_name="Entware"
    local backup_file="$SELECTED_DRIVE/$date/$(get_architecture)-installer.tar.gz"
    
    local source_size_kb=$(du -s /opt | awk '{print $1}')
    check_free_space "$source_size_kb" "$item_name" 1 || return 1

    if ! tar cvzf "$backup_file" -C /opt . >/dev/null 2>/dev/null; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
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

    for path in $CUSTOM_BACKUP_PATHS; do
        cp -r "$path" "$SELECTED_DRIVE/$date/" 2>/dev/null || { error "Ошибка при копировании $path"; return 1; }
    done
}

backup_firmware() {
    local item_name="firmware"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.bin"
    local source_size_kb=20480
    
    check_free_space "$source_size_kb" "$item_name" 1 || return 1

    ndmc -c "copy flash:/$item_name $backup_file" >/dev/null 2>&1 || { error "Ошибка при сохранении $item_name"; return 1; }
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

    mkdir -p "$SELECTED_DRIVE/$date"
    local backup_performed=0

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config && backup_performed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware && backup_performed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware && backup_performed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files && backup_performed=1; }

    if [ "$backup_performed" -eq 0 ]; then
        error "Ни один из вариантов бэкапа не выбран"
        echo "{\"status\": \"error\", \"message\": \"Ни один из вариантов бэкапа не выбран\"}"
        return 1
    fi

    local total_size_kb=$(du -s "$SELECTED_DRIVE/$date" | awk '{print $1}')
    check_free_space "$total_size_kb" "финального архива" 2 || return 1

    local archive_path="$SELECTED_DRIVE/${DEVICE_ID}_$date.tar.gz"
    if tar -czf "$archive_path" -C "$SELECTED_DRIVE" "$date" 2>/dev/null; then
        echo "{\"status\": \"success\", \"archive_path\": \"$archive_path\"}"
    else
        error "Ошибка при создании архива"
        echo "{\"status\": \"error\", \"message\": \"Ошибка при создании архива\"}"
        return 1
    fi
    rm -rf "$SELECTED_DRIVE/$date"
}

main() {
    clean_log "$LOG_FILE"
    get_device_info
    create_backup
}

main
