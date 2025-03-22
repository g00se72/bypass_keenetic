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

success() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $*" >> "$LOG_FILE"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >> "$LOG_FILE"
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

detect_drive() {
    local media_output=$(ndmc -c show media)
    local uuid=""
    local fstype=""
    local free_bytes=""
    local min_space_mb=200

    while IFS= read -r line; do
        case "$line" in
            *"uuid:"*)
                uuid=$(echo "$line" | cut -d ':' -f2- | sed 's/^ *//g')
                ;;
            *"fstype:"*)
                fstype=$(echo "$line" | cut -d ':' -f2- | sed 's/^ *//g')
                ;;
            *"free:"*)
                free_bytes=$(echo "$line" | cut -d ':' -f2- | sed 's/^ *//g')
                ;;
        esac
        if [ -n "$uuid" ] && [ -n "$fstype" ] && [ -n "$free_bytes" ]; then
            if echo "$fstype" | grep -iq "^ntfs$"; then
                free_mb=$((free_bytes / 1024 / 1024))
                if [ "$free_mb" -ge "$min_space_mb" ]; then
                    SELECTED_DRIVE="/tmp/mnt/$uuid"
                    return 0
                fi
            fi
            uuid=""
            fstype=""
            free_bytes=""
        fi
    done <<EOF
$media_output
EOF

    error "Недостаточно свободного места (>= ${min_space_mb}MB)"
    return 1
}

backup_startup_config() {
    local item_name="startup-config"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.txt"
    ndmc -c "copy $item_name $backup_file" >/dev/null 2>&1 && success "$item_name сохранён" || error "Ошибка при сохранении $item_name"
}

backup_entware() {
    local item_name="Entware"
    local backup_file="$SELECTED_DRIVE/$date/$(get_architecture)-installer.tar.gz"
    tar cvzf "$backup_file" -C /opt . 2>&1 | tail -n 2 | grep -iq "error\|no space left on device" \
        && error "Ошибка при сохранении $item_name" || success "$item_name сохранён"
}

backup_custom_files() {
    local item_name="custom-files"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    
    if [ -z "$CUSTOM_BACKUP_PATHS" ]; then
        error "Переменная CUSTOM_BACKUP_PATHS не задана в bot_config.py"
        return 1
    fi

    for path in $CUSTOM_BACKUP_PATHS; do
        cp -r "$path" "$SELECTED_DRIVE/$date/" 2>/dev/null || { error "Ошибка при копировании $path"; return 1; }
    done
    
    success "$item_name сохранён"
}

backup_firmware() {
    local item_name="firmware"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.bin"
    ndmc -c "copy flash:/$item_name $backup_file" >/dev/null 2>&1 && success "$item_name сохранена" || error "Ошибка при сохранении $item_name"
}

create_backup() {
    if [ -z "$SELECTED_DRIVE" ] && ! detect_drive; then
        error "Не удалось определить накопитель для бэкапа"
        return 1
    fi

    mkdir -p "$SELECTED_DRIVE/$date"
    local backup_performed=0

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config; backup_performed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware; backup_performed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware; backup_performed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files; backup_performed=1; }

    if [ "$backup_performed" -eq 0 ]; then
        error "Ни один из вариантов бэкапа не выбран"
        return 1
    fi

    local archive_path="$SELECTED_DRIVE/${DEVICE_ID}_$date.tar.gz"
    tar -czf "$archive_path" -C "$SELECTED_DRIVE" "$date" && success "Архив создан" || { error "Ошибка при создания архива"; return 1; }
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Архив сохранён: $archive_path" >> "$LOG_FILE"
    rm -rf "$SELECTED_DRIVE/$date"
}

main() {
    get_device_info
    create_backup
}

main 2>&1 | tee -a "$LOG_FILE"
