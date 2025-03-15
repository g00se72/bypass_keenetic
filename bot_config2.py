# ВЕРСИЯ СКРИПТА 2.0.0

token = 'MyBotFatherToken'  # Ключ api бота
usernames = ['MySuperLogin']  # Ваш логин в телеграмме без @, не бота. Логин именно Вашей учетной записи в ТГ.

# Заполняются с сайта https://my.telegram.org/apps
# вместо вас запрос будет посылать бот, оттуда и будут запрашиваться ключи
appapiid = 'myapiid'
appapihash = 'myiphash'
routerip = '192.168.1.1'  # ip роутера

# Список vpn для выборочной маршрутизации
vpn_allowed="IKE|SSTP|OpenVPN|Wireguard|L2TP"

# Следующие настройки могут быть оставлены по умолчанию, но можно будет что-то поменять
localportsh = '1082'  # локальный порт для shadowsocks
dnsporttor = '9053'  # чтобы onion сайты открывался через любой браузер - любой открытый порт
localporttor = '9141'  # локальный порт для тор
localportvless = '10810'  # локальный порт для vless
localporttrojan = '10829'  # локальный порт для trojan
dnsovertlsport = '40500'  # можно посмотреть номер порта командой "cat /tmp/ndnproxymain.stat"
dnsoverhttpsport = '40508'  # можно посмотреть номер порта командой "cat /tmp/ndnproxymain.stat"

# Пути к конфигурационным файлам и директориям
paths = {
    "unblock_dir": "/opt/etc/unblock/",
    "tor_config": "/opt/etc/tor/torrc",
    "shadowsocks_config": "/opt/etc/shadowsocks.json",
    "trojan_config": "/opt/etc/trojan/config.json",
    "vless_config": "/opt/etc/xray/config.json",
    "error_log": "/opt/etc/error.log",
    "script_sh": "/opt/root/script.sh",
}

# Команды для перезапуска сервисов
services = {
    "tor_restart": "/opt/etc/init.d/S35tor restart",
    "shadowsocks_restart": "/opt/etc/init.d/S22shadowsocks restart",
    "trojan_restart": "/opt/etc/init.d/S22trojan restart",
    "vless_restart": "/opt/etc/init.d/S24xray restart",
    "unblock_update": "/opt/bin/unblock_update.sh",
    "router_reboot": "ndmc -c system reboot",
    "dns_override_on": "ndmc -c 'opkg dns-override'",
    "dns_override_off": "ndmc -c 'no opkg dns-override'",
    "save_config": "ndmc -c 'system configuration save'",
}

# URL-адреса для скачиваемых файлов
download_urls = {
    "script_sh": "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/script2.sh",
    "info_md": "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/info.md",
    "version_md": "https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/version.md",
}
