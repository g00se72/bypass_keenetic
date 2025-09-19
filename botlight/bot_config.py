# Настройки бота
token = "MyBotFatherToken"  # Ключ api бота
usernames = ["MySuperLogin"]  # Ваш логин в телеграмме без @
MAX_RESTARTS = 5  # Максимальное количество перезапусков бота
RESTART_DELAY = 60  # Задержка в секундах перед перезапуском после ошибки

# Настройки Proxy
proxy0port = 9050  # Локальный порт для Tor socks5 прокси
proxy0interface = "Proxy0"  # Название интерфейса для Tor
proxy1port = 1080  # Локальный порт для xray/singbox
proxy1interface = "Proxy1"  # Название интерфейса для xray и singbox в режиме socks5

# Настройки клиента vless
vless_client = "singbox" # Клиент для установки singbox или xray
client_mode = "tun" # Режим работы singbox tun/socks5 (для xray - всегда socks5)

# Список пакетов
packages = [
    "tor",
    "tor-geoip",
    "obfs4",
    "webtunnel-client",
    "xray",
    "sing-box-go",
    "magitrickle",
    "coreutils-split"
]

# Базовые пути
paths = {
    "bot_dir": "/opt/etc/bot",
    "tor_dir": "/opt/etc/tor", 
    "singbox_dir": "/opt/etc/sing-box",
    "xray_dir": "/opt/etc/xray",
    "keensnap_dir": "/opt/root/KeenSnap",
    "templates_dir": "/opt/etc/bot/templates",
    "init_dir": "/opt/etc/init.d",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt"
}

# Динамическое создание путей на основе базовых путей
paths["bot_path"] = paths["bot_dir"] + "/main.py"
paths["bot_config"] = paths["bot_dir"] + "/bot_config.py"
paths["error_log"] = paths["bot_dir"] + "/error.log"
paths["script_sh"] = paths["bot_dir"] + "/script.sh"
paths["keensnap_path"] = paths["keensnap_dir"] + "/keensnap.sh"
paths["keensnap_log"] = paths["keensnap_dir"] + "/backup.log"
paths["tor_config"] = paths["tor_dir"] + "/torrc"
paths["singbox_config"] = paths["singbox_dir"] + "/config.json"
paths["xray_config"] = paths["xray_dir"] + "/config.json"
paths["init_bot"] = paths["init_dir"] + "/S99telegram_bot"
paths["init_tor"] = paths["init_dir"] + "/S35tor"
paths["init_singbox"] = paths["init_dir"] + "/S99sing-box"
paths["init_xray"] = paths["init_dir"] + "/S24xray"
paths["init_MT"] = paths["init_dir"] + "/S99magitrickle"

# Команды для перезапуска сервисов
services = {
    "service_script": [paths["init_bot"], "restart"],
    "tor_restart": [paths["init_tor"], "restart"],
    "singbox_restart": [paths["init_singbox"], "restart"],
    "xray_restart": [paths["init_xray"], "restart"],
    "MT_restart": [paths["init_MT"], "restart"]
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
        # paths["singbox_config"],
        # paths["xray_config"],
        # paths["tor_config"],
        # paths["script_sh"],
        paths["bot_dir"]
    ])
}
