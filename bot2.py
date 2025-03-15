#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 2.0.0
# ✅ ❌ 🔑 ❗ ⚙️ ‼️ 🤖 🚦 📲 🗑 ⏳ 💡 📑 📄 ⁉️ ➕ ➖ ⛔ 🔄

import asyncio
import subprocess
import os
import time
import telebot
from telebot import types
from telethon.sync import TelegramClient
from urllib.parse import urlparse, parse_qs
import base64
import requests
import bot_config as config

bot = telebot.TeleBot(config.token)
level = 0
selected_file = ""

# Функции для создания меню
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔑 Ключи и мосты", "📑 Списки обхода")
    markup.add("📲 Установка и удаление", "⚙️ Сервис")
    markup.add("💡 Информация")
    return markup

def create_service_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 Перезапустить бота", "⛔ Перезагрузить роутер")
    markup.add("⁉️ DNS Override", "🚦 Перезагрузить сервисы")
    markup.add("🔄 Обновления", "🔙 Назад")
    return markup

def create_install_remove_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📲 Установка", "🗑 Удаление")
    markup.row("🔙 Назад")
    return markup

def create_keys_bridges_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Shadowsocks", "Tor")
    markup.add("Vless", "Trojan")
    markup.add("🔙 Назад")
    return markup

def create_tor_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Tor вручную", "Tor через telegram")
    markup.add("🔙 Назад")
    return markup

def create_bypass_list_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📄 Показать список", "➕ Добавить в список", "➖ Удалить из списка")
    markup.row("🔙 Назад")
    return markup

def create_back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 Назад")
    return markup

def create_dns_override_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ DNS Override ВКЛ", "❌ DNS Override ВЫКЛ")
    markup.add("🔙 Назад")
    return markup

def create_bypass_files_menu():
    dirname = config.paths["unblock_dir"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if os.path.exists(dirname):
        dirfiles = os.listdir(dirname)
        markuplist = [fln.replace(".txt", "") for fln in dirfiles]
        markup.add(*markuplist)
    markup.add("🔙 Назад")
    return markup

# Вспомогательные функции
def download_script():
    os.system(f"curl -s -o {config.paths['script_sh']} {config.download_urls['script_sh']}")
    os.chmod(config.paths["script_sh"], 0o0755)

def send_long_message(chat_id, text, parse_mode=None):
    current_part = ""
    for line in text.split('\n'):
        if len(current_part + '\n' + line) > 4096:
            bot.send_message(chat_id, current_part, parse_mode=parse_mode)
            current_part = line
        else:
            current_part += '\n' + line if current_part else line
    if current_part:
        bot.send_message(chat_id, current_part, parse_mode=parse_mode)

def return_to_main_menu(chat_id):
    global level, selected_file
    level = 0
    selected_file = ""
    bot.send_message(chat_id, '🤖 Добро пожаловать в меню!', reply_markup=create_main_menu())

def set_level_and_reply(chat_id, new_level, text, markup):
    global level
    level = new_level
    bot.send_message(chat_id, text, reply_markup=markup)

# Обработчики уровней
def handle_bypass_files_selection(message):
    dirname = config.paths["unblock_dir"]
    dirfiles = os.listdir(dirname)
    for fln in dirfiles:
        if fln == message.text + '.txt':
            global selected_file
            selected_file = message.text
            set_level_and_reply(message.chat.id, 2, "Меню " + selected_file, create_bypass_list_menu())
            return
    bot.send_message(message.chat.id, "Не найден", reply_markup=create_back_menu())

def handle_bypass_list_menu(message):
    if message.text == "📄 Показать список":
        with open(f"{config.paths['unblock_dir']}{selected_file}.txt", 'r') as f:
            sites = sorted(line.strip() for line in f if line.strip())
        text = "Список пуст" if not sites else "\n".join(sites)
        send_long_message(message.chat.id, text)
        bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=create_bypass_list_menu())
    elif message.text == "➕ Добавить в список":
        set_level_and_reply(message.chat.id, 3, "Введите имя сайта или домена для разблокировки", create_back_menu())
    elif message.text == "➖ Удалить из списка":
        set_level_and_reply(message.chat.id, 4, "Введите имя сайта или домена для удаления", create_back_menu())

def handle_add_to_bypass(message):
    global level
    with open(f"{config.paths['unblock_dir']}{selected_file}.txt", 'r') as f:
        mylist = {line.strip() for line in f}
    k = len(mylist)
    if len(message.text) > 1:
        mylist.update(message.text.split('\n'))
    with open(f"{config.paths['unblock_dir']}{selected_file}.txt", 'w') as f:
        f.write('\n'.join(sorted(mylist)))
    if k != len(mylist):
        bot.send_message(message.chat.id, "✅ Успешно добавлено")
        os.system(config.services["unblock_update"])
    else:
        bot.send_message(message.chat.id, "Было добавлено ранее")
    level = 2
    bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=create_bypass_list_menu())

def handle_remove_from_bypass(message):
    global level
    with open(f"{config.paths['unblock_dir']}{selected_file}.txt", 'r') as f:
        mylist = {line.strip() for line in f}
    k = len(mylist)
    mylist.difference_update(message.text.split('\n'))
    with open(f"{config.paths['unblock_dir']}{selected_file}.txt", 'w') as f:
        f.write('\n'.join(sorted(mylist)))
    if k != len(mylist):
        bot.send_message(message.chat.id, "✅ Успешно удалено")
        os.system(config.services["unblock_update"])
    else:
        bot.send_message(message.chat.id, "Не найдено в списке")
    level = 2
    bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=create_bypass_list_menu())

def handle_keys_bridges_selection(message):
    if message.text == 'Tor':
        set_level_and_reply(message.chat.id, 6, '🤖 Добро пожаловать в меню Tor!', create_tor_menu())
    elif message.text == 'Shadowsocks':
        set_level_and_reply(message.chat.id, 9, "🔑 Скопируйте ключ сюда", create_back_menu())
    elif message.text == 'Vless':
        set_level_and_reply(message.chat.id, 10, "🔑 Скопируйте ключ сюда", create_back_menu())
    elif message.text == 'Trojan':
        set_level_and_reply(message.chat.id, 11, "🔑 Скопируйте ключ сюда", create_back_menu())

def handle_tor_menu(message):
    if message.text == 'Tor вручную':
        set_level_and_reply(message.chat.id, 7, "🔑 Скопируйте ключ сюда", create_back_menu())
    elif message.text == 'Tor через telegram':
        set_level_and_reply(message.chat.id, 8, "Нажмите 'Запросить' для получения мостов через Telegram",
                            types.ReplyKeyboardMarkup(resize_keyboard=True).row("Запросить", "🔙 Назад"))

def handle_tor_manually(message):
    tormanually(message.text)
    os.system(config.services["tor_restart"])
    return_to_main_menu(message.chat.id)

def handle_tor_telegram(message):
    if message.text == "Запросить":
        tor(message.chat.id)
        os.system(config.services["tor_restart"])
        return_to_main_menu(message.chat.id)

def handle_shadowsocks(message):
    shadowsocks(message.text)
    time.sleep(2)
    os.system(config.services["shadowsocks_restart"])
    return_to_main_menu(message.chat.id)

def handle_vless(message):
    vless(message.text)
    os.system(config.services["vless_restart"])
    return_to_main_menu(message.chat.id)

def handle_trojan(message):
    trojan(message.text)
    os.system(config.services["trojan_restart"])
    return_to_main_menu(message.chat.id)

# Словарь обработчиков уровней
level_handlers = {
    1: handle_bypass_files_selection,
    2: handle_bypass_list_menu,
    3: handle_add_to_bypass,
    4: handle_remove_from_bypass,
    5: handle_keys_bridges_selection,
    6: handle_tor_menu,
    7: handle_tor_manually,
    8: handle_tor_telegram,
    9: handle_shadowsocks,
    10: handle_vless,
    11: handle_trojan,
}

# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username not in config.usernames:
        bot.send_message(message.chat.id, 'Вы не являетесь автором канала')
        return
    return_to_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "trigger_update")
def handle_update(call):
    bot.send_message(call.message.chat.id, '⏳ Устанавливаются обновления, подождите!')
    download_script()
    update = subprocess.Popen([config.paths['script_sh'], '-update'], stdout=subprocess.PIPE)
    results = "\n".join(line.decode().strip() for line in update.stdout)
    bot.send_message(call.message.chat.id, results)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.from_user.username not in config.usernames or message.chat.type != 'private':
        bot.send_message(message.chat.id, '🤖 Вы не являетесь автором канала или это не приватный чат')
        return

    global level, selected_file

    if message.text == '🔙 Назад':
        if level in (3, 4):
            level = 2
            bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=create_bypass_list_menu())
        elif level == 2:
            level = 1
            bot.send_message(message.chat.id, "📑 Списки обхода", reply_markup=create_bypass_files_menu())
        elif level in (9, 10, 11):
            level = 5
            bot.send_message(message.chat.id, "🔑 Ключи и мосты", reply_markup=create_keys_bridges_menu())
        elif level in (6, 7, 8):
            if level == 6:
                level = 5
                bot.send_message(message.chat.id, "🔑 Ключи и мосты", reply_markup=create_keys_bridges_menu())
            elif level in (7, 8):
                level = 6
                bot.send_message(message.chat.id, "🤖 Добро пожаловать в меню Tor!", reply_markup=create_tor_menu())
        else:
            return_to_main_menu(message.chat.id)
        return

    menu_commands = {
        '💡 Информация': lambda: bot.send_message(message.chat.id, requests.get(config.download_urls["info_md"]).text, reply_markup=create_main_menu(), parse_mode='Markdown', disable_web_page_preview=True),
        '⚙️ Сервис': lambda: bot.send_message(message.chat.id, '⚙️ Сервисное меню!', reply_markup=create_service_menu()),
        '🤖 Перезапустить бота': lambda: (bot.send_message(message.chat.id, "⏳ Бот будет перезапущен", reply_markup=create_service_menu()), subprocess.Popen([config.paths['script_sh'], '-restart'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)),
        '⛔ Перезагрузить роутер': lambda: (os.system(config.services["router_reboot"]), bot.send_message(message.chat.id, "⏳ Роутер перезагружается!\nЭто займет около 2 минут", reply_markup=create_service_menu())),
        '⁉️ DNS Override': lambda: bot.send_message(message.chat.id, '⁉️ DNS Override', reply_markup=create_dns_override_menu()),
        '✅ DNS Override ВКЛ': lambda: (os.system(config.services["dns_override_on"]), time.sleep(2), os.system(config.services["save_config"]), bot.send_message(message.chat.id, '✅ DNS Override включен!\nРоутер перезагружается...', reply_markup=create_service_menu()), time.sleep(5), os.system(config.services["router_reboot"])),
        '❌ DNS Override ВЫКЛ': lambda: (os.system(config.services["dns_override_off"]), time.sleep(2), os.system(config.services["save_config"]), bot.send_message(message.chat.id, '❌ DNS Override выключен!\nРоутер перезагружается...', reply_markup=create_service_menu()), time.sleep(5), os.system(config.services["router_reboot"])),
        '🚦 Перезагрузить сервисы': lambda: (bot.send_message(message.chat.id, '⏳ Перезагрузка сервисов...'), [os.system(srv) for srv in [config.services["shadowsocks_restart"], config.services["trojan_restart"], config.services["vless_restart"], config.services["tor_restart"]]], bot.send_message(message.chat.id, '✅ Сервисы перезагружены!', reply_markup=create_service_menu())),
        '🔄 Обновления': lambda: handle_updates(message),
        '📑 Списки обхода': lambda: set_level_and_reply(message.chat.id, 1, "📑 Списки обхода", create_bypass_files_menu()),
        '🔑 Ключи и мосты': lambda: set_level_and_reply(message.chat.id, 5, "🔑 Ключи и мосты", create_keys_bridges_menu()),
        '📲 Установка и удаление': lambda: bot.send_message(message.chat.id, '📲 Установка и удаление', reply_markup=create_install_remove_menu()),
        '📲 Установка': lambda: handle_install(message),
        '🗑 Удаление': lambda: handle_remove(message),
    }

    if message.text in menu_commands:
        menu_commands[message.text]()
    elif level in level_handlers:
        level_handlers[level](message)

def handle_updates(message):
    response = requests.get(config.download_urls["version_md"])
    bot_new_version = response.text if response.status_code == 200 else "N/A"
    with open(__file__, encoding='utf-8') as file:
        bot_version = next((line.replace('# ВЕРСИЯ СКРИПТА', '').strip() for line in file if line.startswith('# ВЕРСИЯ СКРИПТА')), "N/A")
    service_update_info = f"*Установленная версия:* {bot_version}\n*Доступная на git версия:* {bot_new_version}"
    if tuple(map(int, bot_version.split("."))) < tuple(map(int, bot_new_version.split("."))):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Обновить", callback_data="trigger_update"))
        bot.send_message(message.chat.id, f"{service_update_info}\nЕсли хотите обновить, нажмите кнопку ниже", reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"{service_update_info}\n\nУ вас уже установлена последняя версия", parse_mode='Markdown')

def handle_install(message):
    download_script()
    install = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE)
    results = "\n".join(line.decode().strip() for line in install.stdout)
    full_message = f"{results}\n\nУстановка завершена. Теперь нужно настроить роутер и перейти к спискам для разблокировок. Ключи для Vless, Shadowsocks и Trojan устанавливаются вручную, для Tor — автоматически: Ключи и Мосты -> Tor -> Tor через Telegram.\n\nДля завершения настройки зайдите в меню Сервис -> DNS Override -> ВКЛ. Роутер перезагрузится, это займёт около 2 минут."
    bot.send_message(message.chat.id, full_message, reply_markup=create_main_menu())
    os.system(config.services["unblock_update"])

def handle_remove(message):
    download_script()
    remove = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE)
    results = "\n".join(line.decode().strip() for line in remove.stdout)
    bot.send_message(message.chat.id, results, reply_markup=create_service_menu())

# Функции обработки ключей
def vless(key):
    url = key[6:]
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    address, id = parsed_url.hostname, parsed_url.username
    port = parsed_url.port or 443
    security, encryption = params.get('security', [''])[0], params.get('encryption', ['none'])[0]
    pbk, headerType = params.get('pbk', [''])[0], params.get('headerType', ['none'])[0]
    fp, spx, flow = params.get('fp', [''])[0], params.get('spx', ['/'])[0], params.get('flow', ['xtls-rprx-vision'])[0]
    sni, sid = params.get('sni', [''])[0], params.get('sid', [''])[0]
    with open(config.paths["vless_config"], 'w') as f:
        sh = (
            f'{{"log":{{"access":"/opt/etc/xray/access.log","error":"/opt/etc/xray/error.log","loglevel":"none"}},'
            f'"inbounds":[{{"port":{config.localportvless},"listen":"::","protocol":"dokodemo-door",'
            f'"settings":{{"network":"tcp","followRedirect":true}},'
            f'"sniffing":{{"enabled":true,"destOverride":["http","tls"]}}}}],'
            f'"outbounds":[{{"tag":"vless-reality","protocol":"vless","settings":{{"vnext":[{{"address":"{address}","port":{port},'
            f'"users":[{{"id":"{id}","flow":"{flow}","encryption":"{encryption}","level":0}}]}}]}},'
            f'"streamSettings":{{"network":"tcp","security":"{security}",'
            f'"realitySettings":{{"publicKey":"{pbk}","fingerprint":"{fp}","serverName":"{sni}",'
            f'"shortId":"{sid}","spiderX":"{spx}"}}}}}},'
            f'{{"tag":"direct","protocol":"freedom"}},'
            f'{{"tag":"block","protocol":"blackhole","settings":{{"response":{{"type":"http"}}}}}}],'
            f'"routing":{{"domainStrategy":"IPIfNonMatch","rules":[{{"type":"field","port":"0-65535","outboundTag":"vless-reality","enabled":true}}]}}'
            f'}}'
        )
        f.write(sh)

def trojan(key):
    key = key.split('//')[1]
    pw = key.split('@')[0]
    key = key.replace(pw + "@", "", 1)
    host = key.split(':')[0]
    key = key.replace(host + ":", "", 1)
    port = key.split('?')[0].split('#')[0]
    with open(config.paths["trojan_config"], 'w') as f:
        sh = (
            f'{{"run_type":"nat",'
            f'"local_addr":"::",'
            f'"local_port":{config.localporttrojan},'
            f'"remote_addr":"{host}",'
            f'"remote_port":{port},'
            f'"password":["{pw}"],'
            f'"ssl":{{"verify":false,"verify_hostname":false}}'
            f'}}'
        )
        f.write(sh)

def shadowsocks(key):
    encodedkey = key.split('//')[1].split('@')[0] + '=='
    password = str(base64.b64decode(encodedkey)[2:].split(':')[1])[:-1]
    server = key.split('@')[1].split('/')[0].split(':')[0]
    port = key.split('@')[1].split('/')[0].split(':')[1].split('#')[0]
    method = str(base64.b64decode(encodedkey).split(':')[0])[2:]
    with open(config.paths["shadowsocks_config"], 'w') as f:
        sh = (
            f'{{"server":["{server}"],'
            f'"mode":"tcp_and_udp",'
            f'"server_port":{port},'
            f'"password":"{password}",'
            f'"timeout":86400,'
            f'"method":"{method}",'
            f'"local_address":"::",'
            f'"local_port":{config.localportsh},'
            f'"fast_open":false,'
            f'"ipv6_first":true'
            f'}}'
        )
        f.write(sh)

def tormanually(bridges):
    with open(config.paths["tor_config"], 'w') as f:
        sh = (
            f'User root\n'
            f'PidFile /opt/var/run/tor.pid\n'
            f'ExcludeExitNodes {{RU}},{{UA}},{{AM}},{{KG}},{{BY}}\n'
            f'StrictNodes 1\n'
            f'TransPort 0.0.0.0:{config.localporttor}\n'
            f'ExitRelay 0\n'
            f'ExitPolicy reject *:*\n'
            f'ExitPolicy reject6 *:*\n'
            f'GeoIPFile /opt/share/tor/geoip\n'
            f'GeoIPv6File /opt/share/tor/geoip6\n'
            f'DataDirectory /opt/tmp/tor\n'
            f'VirtualAddrNetwork 10.254.0.0/16\n'
            f'DNSPort 127.0.0.1:{config.dnsporttor}\n'
            f'AutomapHostsOnResolve 1\n'
            f'UseBridges 1\n'
            f'ClientTransportPlugin obfs4 exec /opt/sbin/obfs4proxy managed\n'
            f'{bridges.replace("obfs4", "Bridge obfs4")}'
        )
        f.write(sh)

async def get_tor_bridges():
    client = TelegramClient('TorBridgeFetcher', config.appapiid, config.appapihash)
    try:
        await client.start(phone=config.phonenumber)
        await client.send_message('GetBridgesBot', '/bridges')
        async for msg in client.iter_messages('GetBridgesBot', limit=1, wait_time=10):
            if msg.text and "Your bridges:" in msg.text:
                return msg.text.replace("Your bridges:\n", "").replace("obfs4", "Bridge obfs4")
    except Exception as e:
        return None
    finally:
        await client.disconnect()
    return None

import asyncio

def tor(chat_id):
    bridges = asyncio.run(get_tor_bridges())
    if bridges:
        with open(config.paths["tor_config"], 'w') as f:
            sh = (
                f'User root\n'
                f'PidFile /opt/var/run/tor.pid\n'
                f'ExcludeExitNodes {{RU}},{{UA}},{{AM}},{{KG}},{{BY}}\n'
                f'StrictNodes 1\n'
                f'TransPort 0.0.0.0:{config.localporttor}\n'
                f'ExitRelay 0\n'
                f'ExitPolicy reject *:*\n'
                f'ExitPolicy reject6 *:*\n'
                f'GeoIPFile /opt/share/tor/geoip\n'
                f'GeoIPv6File /opt/share/tor/geoip6\n'
                f'DataDirectory /opt/tmp/tor\n'
                f'VirtualAddrNetwork 10.254.0.0/16\n'
                f'DNSPort 127.0.0.1:{config.dnsporttor}\n'
                f'AutomapHostsOnResolve 1\n'
                f'UseBridges 1\n'
                f'ClientTransportPlugin obfs4 exec /opt/sbin/obfs4proxy managed\n'
                f'{bridges.replace("obfs4", "Bridge obfs4")}\n'
            )
            f.write(sh)
    else:
        bot.send_message(chat_id, '❌ Не удалось получить мосты Tor')
        raise Exception("Failed to fetch Tor bridges")

try:
    bot.infinity_polling()
except Exception as err:
    with open(config.paths["error_log"], "a") as fl:
        fl.write(f"{str(err)}\n")
