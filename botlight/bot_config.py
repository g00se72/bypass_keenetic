# Настройки бота
token = "MyBotFatherToken"  # Ключ api бота
usernames = ["MySuperLogin"]  # Ваш логин в телеграмме без @
MAX_RESTARTS = 5  # Максимальное количество перезапусков бота
RESTART_DELAY = 60  # Задержка в секундах перед перезапуском после ошибки

# Настройки Proxy
proxy0port = 9050  # Локальный порт для Tor socks5 прокси
proxy0interface = "Proxy0"  # Название интерфейса
proxy1port = 1080  # Локальный порт для xray/sing-box
proxy1interface = "Proxy1"  # Название интерфейса

# Настройки клиента vless
vless_client = "sing-box" # Клиент для установки sing-box или xray
client_mode = "socks5" # Режим работы sing-box tun (с gvisor) или socks5, для xray - всегда socks5

# Список пакетов
packages = [
    "tor",
    "tor-geoip",
    "bind-dig",
    "obfs4",
    "webtunnel-client",
    "xray",
    "sing-box-go",
    "magitrickle"
]

# Пути к конфигурационным файлам и директориям
paths = {
    "bot_config": "/opt/etc/bot/bot_config.py",
    "tor_config": "/opt/etc/tor/torrc",
    "sing-box_config": "/opt/etc/sing-box/config.json",
    "xray_config": "/opt/etc/xray/config.json",
    "error_log": "/opt/etc/bot/error.log",
    "keensnap_log": "/opt/root/KeenSnap/backup.log",
    "keensnap": "/opt/root/KeenSnap/keensnap.sh",
    "bot_path": "/opt/etc/bot/main.py",
    "script_sh": "/opt/root/script.sh",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt",
    "init_sing-box": "/opt/etc/init.d/S99sing-box",
    "init_xray": "/opt/etc/init.d/S24xray",
    "init_tor": "/opt/etc/init.d/S35tor",
    "init_bot": "/opt/etc/init.d/S99telegram_bot",
    "init_MT": "/opt/etc/init.d/S99magitrickle",
    "bot_dir": "/opt/etc/bot",
    "templates_dir": "/opt/etc/bot/templates",
    "keensnap_dir": "/opt/root/KeenSnap",
    "tor_dir": "/opt/etc/tor",
    "sing-box_dir": "/opt/etc/sing-box",
    "xray_dir": "/opt/etc/xray"
}

# Команды для перезапуска сервисов
services = {
    "tor_restart": [paths["init_tor"], "restart"],
    "sing-box_restart": [paths["init_sing-box"], "restart"],
    "xray_restart": [paths["init_xray"], "restart"],
    "MR_restart": [paths["init_MT"], "restart"],
    "service_script": [paths["init_bot"], "restart"]
}

# Базовые URL-адреса для скачиваемых файлов
base_url = "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main"
bot_url = f"{base_url}/botlight"
MT_url = "http://bin.magitrickle.dev/packages/add_repo.sh"

# Настройка бэкапа
backup_settings = {
    "LOG_FILE": paths["keensnap_log"],
    "MAX_SIZE_MB": 45,
    "CUSTOM_BACKUP_PATHS":" ".join([
        paths["bot_dir"],
        paths["sing-box_config"],
        paths["xray_config"],
        paths["tor_config"],
        paths["script_sh"]
    ])
}
