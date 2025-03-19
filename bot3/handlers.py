import subprocess
import requests
import os
from telebot import types
from urllib.parse import urlparse, parse_qs
import base64
import bot_config as config
from menu import (
    MENU_MAIN, MENU_BYPASS_FILES, MENU_BYPASS_LIST, MENU_ADD_BYPASS, MENU_REMOVE_BYPASS,
    MENU_KEYS_BRIDGES, MENU_TOR, MENU_SHADOWSOCKS, MENU_VLESS, MENU_TROJAN,
    MENU_SERVICE, MENU_DNS_OVERRIDE, MENU_INSTALL_REMOVE, create_bypass_files_menu
)
from utils import (
    download_script, send_long_message, load_bypass_list, save_bypass_list,
    update_service, toggle_dns_override
)

class BotState:
    def __init__(self):
        self.current_menu = MENU_MAIN
        self.selected_file = ""

def setup_handlers(bot):
    state = BotState()
    
    def set_menu_and_reply(chat_id, new_menu, text=None):
        state.current_menu = new_menu
        if not text:
            text = new_menu.name
        bot.send_message(chat_id, text, reply_markup=new_menu.markup)
    
    def go_to_bypass_files(chat_id):
        create_bypass_files_menu()
        set_menu_and_reply(chat_id, MENU_BYPASS_FILES)

    # Обработчики действий
    def handle_bypass_files_selection(message):
        state.selected_file = message.text
        set_menu_and_reply(message.chat.id, MENU_BYPASS_LIST, "Меню " + state.selected_file)

    def handle_bypass_list_menu(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        if message.text == "📄 Показать список":
            sites = sorted(load_bypass_list(filepath))
            text = "Список пуст" if not sites else "\n".join(sites)
            send_long_message(bot, message.chat.id, text)
            bot.send_message(message.chat.id, "Меню " + state.selected_file, reply_markup=MENU_BYPASS_LIST.markup)
        elif message.text == "➕ Добавить в список":
            set_menu_and_reply(message.chat.id, MENU_ADD_BYPASS, "Введите сайт, домен или IP-адресс для добавления")
        elif message.text == "➖ Удалить из списка":
            set_menu_and_reply(message.chat.id, MENU_REMOVE_BYPASS, "Введите сайт, домен или IP-адресс для удаления")

    def handle_add_to_bypass(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        if len(message.text) > 1:
            mylist.update(message.text.split('\n'))
        save_bypass_list(filepath, mylist)
        if k != len(mylist):
            bot.send_message(message.chat.id, "✅ Успешно добавлено, применяю изменения...")
            os.system(config.services["unblock_update"])
        else:
            bot.send_message(message.chat.id, "❕Было добавлено ранее")
        set_menu_and_reply(message.chat.id, MENU_BYPASS_LIST, "Меню " + state.selected_file)

    def handle_remove_from_bypass(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        mylist.difference_update(message.text.split('\n'))
        save_bypass_list(filepath, mylist)
        if k != len(mylist):
            bot.send_message(message.chat.id, "✅ Успешно удалено, применяю изменения...")
            os.system(config.services["unblock_update"])
        else:
            bot.send_message(message.chat.id, "❕Не найдено в списке")
        set_menu_and_reply(message.chat.id, MENU_BYPASS_LIST, "Меню " + state.selected_file)

    def handle_keys_bridges_selection(message):
        if message.text == 'Tor':
            set_menu_and_reply(message.chat.id, MENU_TOR, "🔑 Скопируйте мосты сюда")
        elif message.text == 'Shadowsocks':
            set_menu_and_reply(message.chat.id, MENU_SHADOWSOCKS, "🔑 Скопируйте ключ сюда")
        elif message.text == 'Vless':
            set_menu_and_reply(message.chat.id, MENU_VLESS, "🔑 Скопируйте ключ сюда")
        elif message.text == 'Trojan':
            set_menu_and_reply(message.chat.id, MENU_TROJAN, "🔑 Скопируйте ключ сюда")

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
        with open(config.paths["vless_config"], 'w', encoding='utf-8') as f:
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
        with open(config.paths["trojan_config"], 'w', encoding='utf-8') as f:
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
        with open(config.paths["shadowsocks_config"], 'w', encoding='utf-8') as f:
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
        with open(config.paths["tor_config"], 'w', encoding='utf-8') as f:
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
        set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)

    def handle_shadowsocks(message):
        update_service(bot, message.chat.id, "Shadowsocks", 
                       lambda: shadowsocks_config(message.text), 
                       config.services["shadowsocks_restart"])
        set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)

    def handle_vless(message):
        update_service(bot, message.chat.id, "Vless", 
                       lambda: vless_config(message.text), 
                       config.services["vless_restart"])
        set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)

    def handle_trojan(message):
        update_service(bot, message.chat.id, "Trojan", 
                       lambda: trojan_config(message.text), 
                       config.services["trojan_restart"])
        set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)

    # Словарь переходов и действий
    MENU_TRANSITIONS = {
        '🔙 Назад': lambda chat_id: (
        set_menu_and_reply(chat_id, next(
            (m for m in [MENU_MAIN, MENU_BYPASS_FILES, MENU_BYPASS_LIST, MENU_ADD_BYPASS, MENU_REMOVE_BYPASS,
                         MENU_KEYS_BRIDGES, MENU_TOR, MENU_SHADOWSOCKS, MENU_VLESS, MENU_TROJAN,
                         MENU_SERVICE, MENU_DNS_OVERRIDE, MENU_INSTALL_REMOVE]
             if m.level == state.current_menu.back_level), MENU_MAIN))
        ),
        '💡 Информация': lambda chat_id: bot.send_message(chat_id, requests.get(config.download_urls["info_md"]).text, reply_markup=MENU_MAIN.markup, parse_mode='Markdown', disable_web_page_preview=True),
        '📑 Списки обхода': go_to_bypass_files,
        '🔑 Ключи и мосты': lambda chat_id: set_menu_and_reply(chat_id, MENU_KEYS_BRIDGES),
        '⚙️ Сервис': lambda chat_id: set_menu_and_reply(chat_id, MENU_SERVICE),
        '🤖 Перезапуск бота': lambda chat_id: (
            bot.send_message(chat_id, "⏳ Бот будет перезапущен!\nЭто займет около 15-30 секунд", reply_markup=MENU_SERVICE.markup),
            subprocess.Popen([config.paths['script_sh'], '-restart'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        ),
        '⛔ Перезапуск роутера': lambda chat_id: (
            bot.send_message(chat_id, "⏳ Роутер будет перезапущен!\nЭто займет около 2 минут", reply_markup=MENU_SERVICE.markup),
            os.system(config.services["router_reboot"])
        ),
        '⁉️ DNS Override': lambda chat_id: set_menu_and_reply(chat_id, MENU_DNS_OVERRIDE),
        '✅ DNS Override ВКЛ': lambda chat_id: toggle_dns_override(bot, chat_id, True),
        '❌ DNS Override ВЫКЛ': lambda chat_id: toggle_dns_override(bot, chat_id, False),
        '🚦 Перезапуск сервисов': lambda chat_id: (
            bot.send_message(chat_id, '⏳ Сервисы будут перезапущены!\nЭто займет около 10-15 секунд'),
            update_service(bot, chat_id, "Shadowsocks", lambda: None, config.services["shadowsocks_restart"]),
            update_service(bot, chat_id, "Tor", lambda: None, config.services["tor_restart"]),
            update_service(bot, chat_id, "Vless", lambda: None, config.services["vless_restart"]),
            update_service(bot, chat_id, "Trojan", lambda: None, config.services["trojan_restart"]),
            bot.send_message(chat_id, '❕ Перезапуск сервисов завершен', reply_markup=MENU_MAIN.markup)
        ),
        '🔄 Обновления': lambda chat_id: handle_updates(chat_id),
        '📲 Установка и удаление': lambda chat_id: set_menu_and_reply(chat_id, MENU_INSTALL_REMOVE),
        '📲 Установка': lambda chat_id: handle_install(chat_id),
        '🗑 Удаление': lambda chat_id: handle_remove(chat_id),
    }

    LEVEL_HANDLERS = {
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

    @bot.message_handler(commands=['start'])
    def start(message):
        if message.from_user.username not in config.usernames:
            bot.send_message(message.chat.id, '⚠️ Вы не являетесь автором канала!')
            return
        set_menu_and_reply(message.chat.id, MENU_MAIN)

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
            bot.send_message(message.chat.id, '⚠️ Вы не являетесь автором канала или это не приватный чат!')
            return

        if message.text in MENU_TRANSITIONS:
            MENU_TRANSITIONS[message.text](message.chat.id)
        elif state.current_menu.level in LEVEL_HANDLERS:
            LEVEL_HANDLERS[state.current_menu.level](message)

    def handle_updates(chat_id):
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
                    markup.add(types.InlineKeyboardButton("🔄 Обновить", callback_data="trigger_update"))
                    bot.send_message(chat_id, f"{service_update_info}\nЕсли хотите обновить, нажмите кнопку ниже", reply_markup=markup, parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, f"{service_update_info}\nУ вас уже установлена последняя версия", parse_mode='Markdown')
            except ValueError:
                bot.send_message(chat_id, f"{service_update_info}\nОшибка: версии имеют неверный формат", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"{service_update_info}\nНе удалось проверить обновления", parse_mode='Markdown')

    def handle_install(chat_id):
        download_script()
        install = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE)
        results = "\n".join(line.decode().strip() for line in install.stdout)
        full_message = f"{results}\n\nУстановка завершена. Теперь нужно настроить роутер и перейти к спискам для разблокировок. Ключи устанавливаются вручную - Ключи и Мосты -> Tor, Vless, Shadowsocks, Trojan.\n\nДля завершения настройки зайдите в меню Сервис -> DNS Override -> ВКЛ. Роутер перезагрузится, это займёт около 2 минут"
        bot.send_message(chat_id, full_message, reply_markup=MENU_MAIN.markup)

    def handle_remove(chat_id):
        download_script()
        remove = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE)
        results = "\n".join(line.decode().strip() for line in remove.stdout)
        bot.send_message(chat_id, results, reply_markup=MENU_SERVICE.markup)
