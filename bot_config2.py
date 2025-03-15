token = "YOUR_BOT_TOKEN"
appapiid = YOUR_APP_API_ID
appapihash = "YOUR_APP_API_HASH"
usernames = ["YOUR_USERNAME"]
routerip = "YOUR_ROUTER_IP"
localportsh = 1080
localporttor = 9040
localporttrojan = 1081
localportvless = 1082
dnsporttor = 9053
dnsovertlsport = 853
dnsoverhttpsport = 443

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
