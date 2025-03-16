import subprocess
import requests
import os
from telebot import types
from urllib.parse import urlparse, parse_qs
import base64
import bot_config as config
from menu import MENU_CACHE
from menu import create_bypass_files_menu
from utils import (
    download_script, send_long_message, load_bypass_list, save_bypass_list,
    update_service, return_to_main_menu
)

def setup_handlers(bot, level, selected_file):
#Настройка всех обработчиков

    def set_level_and_reply(chat_id, new_level, text, markup):
        nonlocal level
        level = new_level
        bot.send_message(chat_id, text, reply_markup=markup)
        return level

    # Обработчики уровней
    def handle_bypass_files_selection(message):
        nonlocal selected_file
        dirname = config.paths["unblock_dir"]
        dirfiles = os.listdir(dirname)
        for fln in dirfiles:
            if fln == message.text + '.txt':
                selected_file = message.text
                set_level_and_reply(message.chat.id, 2, "Меню " + selected_file, MENU_CACHE["bypass_list"])
                return
        bot.send_message(message.chat.id, "Не найден", reply_markup=create_bypass_files_menu())

    def handle_bypass_list_menu(message):
        filepath = f"{config.paths['unblock_dir']}{selected_file}.txt"
        if message.text == "📄 Показать список":
            sites = sorted(load_bypass_list(filepath))
            text = "Список пуст" if not sites else "\n".join(sites)
            send_long_message(bot, message.chat.id, text)
            bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=MENU_CACHE["bypass_list"])
        elif message.text == "➕ Добавить в список":
            set_level_and_reply(message.chat.id, 3, "Введите имя сайта или домена для разблокировки", MENU_CACHE["back"])
        elif message.text == "➖ Удалить из списка":
            set_level_and_reply(message.chat.id, 4, "Введите имя сайта или домена для удаления", MENU_CACHE["back"])

    def handle_add_to_bypass(message):
        nonlocal level
        filepath = f"{config.paths['unblock_dir']}{selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        if len(message.text) > 1:
            mylist.update(message.text.split('\n'))
        save_bypass_list(filepath, mylist)
        if k != len(mylist):
            bot.send_message(message.chat.id, "✅ Успешно добавлено")
            os.system(config.services["unblock_update"])
        else:
            bot.send_message(message.chat.id, "Было добавлено ранее")
        level = 2
        bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=MENU_CACHE["bypass_list"])

    def handle_remove_from_bypass(message):
        nonlocal level
        filepath = f"{config.paths['unblock_dir']}{selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        mylist.difference_update(message.text.split('\n'))
        save_bypass_list(filepath, mylist)
        if k != len(mylist):
            bot.send_message(message.chat.id, "✅ Успешно удалено")
            os.system(config.services["unblock_update"])
        else:
            bot.send_message(message.chat.id, "Не найдено в списке")
        level = 2
        bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=MENU_CACHE["bypass_list"])

    def handle_keys_bridges_selection(message):
        if message.text == 'Tor':
            set_level_and_reply(message.chat.id, 8, "🔑 Скопируйте мосты сюда", MENU_CACHE["back"])
        elif message.text == 'Shadowsocks':
            set_level_and_reply(message.chat.id, 9, "🔑 Скопируйте ключ сюда", MENU_CACHE["back"])
        elif message.text == 'Vless':
            set_level_and_reply(message.chat.id, 10, "🔑 Скопируйте ключ сюда", MENU_CACHE["back"])
        elif message.text == 'Trojan':
            set_level_and_reply(message.chat.id, 11, "🔑 Скопируйте ключ сюда", MENU_CACHE["back"])

    # Функции конфигурации сервисов
    def vless_config(key):
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

    def trojan_config(key):
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

    def shadowsocks_config(key):
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

    def tor_config(bridges):
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

    # Обработчики сервисов
    def handle_tor_manually(message):
        update_service(bot, message.chat.id, "Tor", 
                       lambda: tor_config(message.text), 
                       config.services["tor_restart"])

    def handle_shadowsocks(message):
        update_service(bot, message.chat.id, "Shadowsocks", 
                       lambda: shadowsocks_config(message.text), 
                       config.services["shadowsocks_restart"])

    def handle_vless(message):
        update_service(bot, message.chat.id, "Vless", 
                       lambda: vless_config(message.text), 
                       config.services["vless_restart"])

    def handle_trojan(message):
        update_service(bot, message.chat.id, "Trojan", 
                       lambda: trojan_config(message.text), 
                       config.services["trojan_restart"])

    level_handlers = {
        1: handle_bypass_files_selection,
        2: handle_bypass_list_menu,
        3: handle_add_to_bypass,
        4: handle_remove_from_bypass,
        5: handle_keys_bridges_selection,
        8: handle_tor_manually,
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
        nonlocal level, selected_file
        level, selected_file = return_to_main_menu(bot, message.chat.id, level, selected_file)

    @bot.callback_query_handler(func=lambda call: call.data == "trigger_update")
    def handle_update(call):
        bot.send_message(call.message.chat.id, '⏳ Устанавливаются обновления, подождите!')
        download_script()
        update = subprocess.Popen([config.paths['script_sh'], '-update'], stdout=subprocess.PIPE)
        results = "\n".join(line.decode().strip() for line in update.stdout)
        bot.send_message(call.message.chat.id, results)

    @bot.message_handler(content_types=['text'])
    def bot_message(message):
        nonlocal level, selected_file
        if message.from_user.username not in config.usernames or message.chat.type != 'private':
            bot.send_message(message.chat.id, '🤖 Вы не являетесь автором канала или это не приватный чат')
            return

        if message.text == '🔙 Назад':
            if level in (3, 4):
                level = 2
                bot.send_message(message.chat.id, "Меню " + selected_file, reply_markup=MENU_CACHE["bypass_list"])
            elif level == 2:
                level = 1
                bot.send_message(message.chat.id, "📑 Списки обхода", reply_markup=create_bypass_files_menu())
            elif level in (8, 9, 10, 11):
                level = 5
                bot.send_message(message.chat.id, "🔑 Ключи и мосты", reply_markup=MENU_CACHE["keys_bridges"])
            else:
                level, selected_file = return_to_main_menu(bot, message.chat.id, level, selected_file)
            return

        menu_commands = {
            '💡 Информация': lambda: bot.send_message(message.chat.id, requests.get(config.download_urls["info_md"]).text, reply_markup=MENU_CACHE["main"], parse_mode='Markdown', disable_web_page_preview=True),
            '⚙️ Сервис': lambda: bot.send_message(message.chat.id, '⚙️ Сервисное меню!', reply_markup=MENU_CACHE["service"]),
            '🤖 Перезапустить бота': lambda: (bot.send_message(message.chat.id, "⏳ Бот будет перезапущен", reply_markup=MENU_CACHE["service"]), subprocess.Popen([config.paths['script_sh'], '-restart'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)),
            '⛔ Перезагрузить роутер': lambda: (os.system(config.services["router_reboot"]), bot.send_message(message.chat.id, "⏳ Роутер перезагружается!\nЭто займет около 2 минут", reply_markup=MENU_CACHE["service"])),
            '⁉️ DNS Override': lambda: bot.send_message(message.chat.id, '⁉️ DNS Override', reply_markup=MENU_CACHE["dns_override"]),
            '✅ DNS Override ВКЛ': lambda: (os.system(config.services["dns_override_on"]), os.system(config.services["save_config"]), bot.send_message(message.chat.id, '✅ DNS Override включен!\nРоутер перезагружается...', reply_markup=MENU_CACHE["service"]), os.system(config.services["router_reboot"])),
            '❌ DNS Override ВЫКЛ': lambda: (os.system(config.services["dns_override_off"]), os.system(config.services["save_config"]), bot.send_message(message.chat.id, '❌ DNS Override выключен!\nРоутер перезагружается...', reply_markup=MENU_CACHE["service"]), os.system(config.services["router_reboot"])),
            '🚦 Перезагрузить сервисы': lambda: (bot.send_message(message.chat.id, '⏳ Перезагрузка сервисов...'), [os.system(srv) for srv in [config.services["shadowsocks_restart"], config.services["trojan_restart"], config.services["vless_restart"], config.services["tor_restart"]]], bot.send_message(message.chat.id, '✅ Сервисы перезагружены!', reply_markup=MENU_CACHE["service"])),
            '🔄 Обновления': lambda: handle_updates(message),
            '📑 Списки обхода': lambda: set_level_and_reply(message.chat.id, 1, "📑 Списки обхода", create_bypass_files_menu()),
            '🔑 Ключи и мосты': lambda: set_level_and_reply(message.chat.id, 5, "🔑 Ключи и мосты", MENU_CACHE["keys_bridges"]),
            '📲 Установка и удаление': lambda: bot.send_message(message.chat.id, '📲 Установка и удаление', reply_markup=MENU_CACHE["install_remove"]),
            '📲 Установка': lambda: handle_install(message),
            '🗑 Удаление': lambda: handle_remove(message),
        }

        if message.text in menu_commands:
            menu_commands[message.text]()
        elif level in level_handlers:
            level_handlers[level](message)

    def handle_updates(message):
        response = requests.get(config.download_urls["version_md"])
        bot_new_version = response.text.strip() if response.status_code == 200 else "N/A"
        
        main_file_path = os.path.join(os.path.dirname(__file__), "main.py")
        with open(main_file_path, encoding='utf-8') as file:
            bot_version = next((line.replace('# ВЕРСИЯ СКРИПТА', '').strip() for line in file if line.startswith('# ВЕРСИЯ СКРИПТА')), "N/A")
        
        service_update_info = f"*Установленная версия:* {bot_version}\n*Доступная на git версия:* {bot_new_version}"
        
        if bot_version != "N/A" and bot_new_version != "N/A":
            try:
                if tuple(map(int, bot_version.split("."))) < tuple(map(int, bot_new_version.split("."))):
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("Обновить", callback_data="trigger_update"))
                    bot.send_message(message.chat.id, f"{service_update_info}\nЕсли хотите обновить, нажмите кнопку ниже", reply_markup=markup, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, f"{service_update_info}\n\nУ вас уже установлена последняя версия", parse_mode='Markdown')
            except ValueError:
                bot.send_message(message.chat.id, f"{service_update_info}\n\nОшибка: версии имеют неверный формат", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"{service_update_info}\n\nНе удалось проверить обновления", parse_mode='Markdown')

    def handle_install(message):
        download_script()
        install = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE)
        results = "\n".join(line.decode().strip() for line in install.stdout)
        full_message = f"{results}\n\nУстановка завершена. Теперь нужно настроить роутер и перейти к спискам для разблокировок. Ключи устанавливаются вручную - Ключи и Мосты -> Tor, Vless, Shadowsocks, Trojan.\n\nДля завершения настройки зайдите в меню Сервис -> DNS Override -> ВКЛ. Роутер перезагрузится, это займёт около 2 минут."
        bot.send_message(message.chat.id, full_message, reply_markup=MENU_CACHE["main"])
        os.system(config.services["unblock_update"])

    def handle_remove(message):
        download_script()
        remove = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE)
        results = "\n".join(line.decode().strip() for line in remove.stdout)
        bot.send_message(message.chat.id, results, reply_markup=MENU_CACHE["service"])
