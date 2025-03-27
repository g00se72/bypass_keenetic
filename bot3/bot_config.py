# ВЕРСИЯ СКРИПТА 3.3.4

# Настройки бота
token = 'MyBotFatherToken'  # Ключ api бота
usernames = ['MySuperLogin']  # Ваш логин в телеграмме без @
MAX_RESTARTS = 5  # Максимальное количество перезапусков бота
RESTART_DELAY = 60  # Задержка в секундах перед перезапуском после ошибки

# IP роутера
routerip = '192.168.1.1'

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

# Список пакетов
packages = [
    "tor",
    "tor-geoip",
    "bind-dig",
    "cron",
    "dnsmasq-full",
    "ipset",
    "iptables",
    "obfs4",
    "shadowsocks-libev-ss-redir",
    "shadowsocks-libev-config",
    "xray",
    "trojan",
    "coreutils-split"
]

# Пути к конфигурационным файлам и директориям
paths = {
    "unblock_dir": "/opt/etc/unblock/",
    "tor_config": "/opt/etc/tor/torrc",
    "shadowsocks_config": "/opt/etc/shadowsocks.json",
    "trojan_config": "/opt/etc/trojan/config.json",
    "vless_config": "/opt/etc/xray/config.json",
    "templates_dir": "/opt/etc/bot/templates/",
    "dnsmasq_conf": "/opt/etc/dnsmasq.conf",
    "crontab": "/opt/etc/crontab",
    "redirect_script": "/opt/etc/ndm/netfilter.d/100-redirect.sh",
    "vpn_script": "/opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh",
    "ipset_script": "/opt/etc/ndm/fs.d/100-ipset.sh",
    "unblock_ipset": "/opt/bin/unblock_ipset.sh",
    "unblock_dnsmasq": "/opt/bin/unblock_dnsmasq.sh",
    "unblock_update": "/opt/bin/unblock_update.sh",
    "keensnap_dir": "/opt/root/KeenSnap/",
    "script_bu": "/opt/root/KeenSnap/keensnap.sh",
    "bot_dir": "/opt/etc/bot",
    "bot_path": "/opt/etc/bot/main.py",
    "bot_config": "/opt/etc/bot/bot_config.py",
    "hosts_file": "/opt/etc/hosts",
    "error_log": "/opt/etc/bot/error.log",
    "log_bu": "/opt/root/KeenSnap/backup.log",
    "script_sh": "/opt/root/script.sh",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt",
    "init_shadowsocks": "/opt/etc/init.d/S22shadowsocks",
    "init_trojan": "/opt/etc/init.d/S22trojan",
    "init_xray": "/opt/etc/init.d/S24xray",
    "init_tor": "/opt/etc/init.d/S35tor",
    "init_dnsmasq": "/opt/etc/init.d/S56dnsmasq",
    "init_unblock": "/opt/etc/init.d/S99unblock",
    "init_bot": "/opt/etc/init.d/S99telegram_bot",
    "tor_tmp_dir": "/opt/tmp/tor",
    "tor_dir": "/opt/etc/tor",
    "xray_dir": "/opt/etc/xray",
    "trojan_dir": "/opt/etc/trojan"
}

# Команды для перезапуска сервисов
services = {
    "tor_restart": [paths["init_tor"], "restart"],
    "shadowsocks_restart": [paths["init_shadowsocks"], "restart"],
    "trojan_restart": [paths["init_trojan"], "restart"],
    "vless_restart": [paths["init_xray"], "restart"],
    "service_script": [paths["init_bot"], "restart"],
    "unblock_update": [paths["unblock_update"]],
    "router_reboot": ["ndmc", "-c", "system", "reboot"],
    "dns_override_on": ["ndmc", "-c", "opkg dns-override"],
    "dns_override_off": ["ndmc", "-c", "no opkg dns-override"],
    "save_config": ["ndmc", "-c", "system configuration save"],
}

# URL-адреса для скачиваемых файлов
base_url = "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main"
bot_url = f"{base_url}/bot3"

download_urls = {
    "script_sh": f"{bot_url}/script.sh",
    "version_md": f"{bot_url}/version.md",
    "dnsmasq_conf": f"{base_url}/dnsmasq.conf",
    "crontab": f"{base_url}/crontab",
    "redirect_script": f"{base_url}/100-redirect.sh",
    "vpn_script_v3": f"{base_url}/100-unblock-vpn.sh",
    "vpn_script_v4": f"{base_url}/100-unblock-vpn-v4.sh",
    "ipset_script": f"{base_url}/100-ipset.sh",
    "keensnap_script": f"{base_url}/KeenSnap/keensnap.sh",
    "tor_template": f"{base_url}/tor_template.torrc",
    "vless_template": f"{base_url}/vless_template.json",
    "trojan_template": f"{base_url}/trojan_template.json",
    "shadowsocks_template": f"{base_url}/shadowsocks_template.json"
}

# Настройка бэкапа
backup_settings = {
    "LOG_FILE": paths["log_bu"],
    "MAX_SIZE_MB": 45,
    "CUSTOM_BACKUP_PATHS":" ".join([
        paths["bot_dir"],
        paths["vless_config"],
        paths["tor_config"],
        paths["script_sh"],
        paths["script_bu"],
    ]),
    "DELETE_ARCHIVE_AFTER_BACKUP": True
}
