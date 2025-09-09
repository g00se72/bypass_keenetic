# Настройки бота
token = 'MyBotFatherToken'  # Ключ api бота
usernames = ['MySuperLogin']  # Ваш логин в телеграмме без @
MAX_RESTARTS = 5  # Максимальное количество перезапусков бота
RESTART_DELAY = 60  # Задержка в секундах перед перезапуском после ошибки

# Настройки Proxy
proxy0port = 9050  # Локальный порт для Tor socks5 прокси
proxy0interface = Proxy0  # Название интерфейса
proxy1port = 1080  # Локальный порт для xray/sing-box
proxy1interface = Proxy1  # Название интерфейса

# Настройки клиента vless
client = sing-box # Какой клиент будет установлен sing-box или xray
mode = socks5 # Режим работы sing-box tun (с gvisor) или socks5, для xray - всегда socks5

# Список пакетов
packages = [
    "tor",
    "tor-geoip",
    "bind-dig",
    "obfs4",
    "webtunnel-client",
    "xray",
    "sing-box-go"
]
