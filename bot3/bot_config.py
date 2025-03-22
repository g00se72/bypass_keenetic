# ВЕРСИЯ СКРИПТА 3.2.4

# Настройки бота
token = 'MyBotFatherToken'  # Ключ api бота
usernames = ['MySuperLogin']  # Ваш логин в телеграмме без @
MAX_RESTARTS = 5  # Максимальное количество перезапусков бота
RESTART_DELAY = 60  # Задержка в секундах перед перезапуском после ошибки

routerip = '192.168.1.1'  # IP роутера

# Список vpn для выборочной маршрутизации
vpn_allowed = "IKE|SSTP|OpenVPN|Wireguard|L2TP"

# Локальные порты
localportsh = 1082  # локальный порт для shadowsocks
dnsporttor = 9053  # чтобы onion сайты открывался через любой браузер - любой открытый порт
localporttor = 9141  # локальный порт для тор
localportvless = 10810  # локальный порт для vless
localporttrojan = 10829  # локальный порт для trojan
dnsovertlsport = 40500  # можно посмотреть номер порта командой "cat /tmp/ndnproxymain.stat"
dnsoverhttpsport = 40508  # можно посмотреть номер порта командой "cat /tmp/ndnproxymain.stat"

# Пути к конфигурационным файлам и директориям
paths = {
    "unblock_dir": "/opt/etc/unblock/",
    "tor_config": "/opt/etc/tor/torrc",
    "shadowsocks_config": "/opt/etc/shadowsocks.json",
    "trojan_config": "/opt/etc/trojan/config.json",
    "vless_config": "/opt/etc/xray/config.json",
    "error_log": "/opt/etc/bot/error.log",
    "log_bu": "/opt/root/KeenSnap/backup.log",
    "script_sh": "/opt/root/script.sh",
    "script_bu": "/opt/root/KeenSnap/keensnap.sh",
    "pid_path": "/opt/var/run/bot.pid",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt",
    "templates_dir": "/opt/etc/bot/templates/"
}

# Настройка бэкапа
# скриптом будет автоматически выбран ntfs накопитель в SELECT DRIVE
backup_settings = {
    "LOG_FILE": paths["log_bu"],
    "SELECTED_DRIVE": "",
    "BACKUP_STARTUP_CONFIG": False,
    "BACKUP_FIRMWARE": False,
    "BACKUP_ENTWARE": False,
    "BACKUP_CUSTOM_FILES": False,
    "CUSTOM_BACKUP_PATHS":" ".join([
        "/opt/etc/bot",
        paths["vless_config"],
        paths["tor_config"],
    ]),
    "DELETE_ARCHIVE_AFTER_BACKUP": False
}

# Команды для перезапуска сервисов
services = {
    "tor_restart": ["/opt/etc/init.d/S35tor", "restart"],
    "shadowsocks_restart": ["/opt/etc/init.d/S22shadowsocks", "restart"],
    "trojan_restart": ["/opt/etc/init.d/S22trojan", "restart"],
    "vless_restart": ["/opt/etc/init.d/S24xray", "restart"],
    "unblock_update": ["/opt/bin/unblock_update.sh"],
    "router_reboot": ["ndmc", "-c", "system", "reboot"],
    "dns_override_on": ["ndmc", "-c", "opkg dns-override"],
    "dns_override_off": ["ndmc", "-c", "no opkg dns-override"],
    "save_config": ["ndmc", "-c", "system configuration save"],
}

# URL-адреса для скачиваемых файлов
download_urls = {
    "script_sh": "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/script.sh",
    "version_md": "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/version.md",
}
