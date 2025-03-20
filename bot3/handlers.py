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
    download_script, load_bypass_list, save_bypass_list, vless_config, trojan_config,
    shadowsocks_config, tor_config
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

    def handle_bypass_files_selection(message):
        state.selected_file = message.text
        set_menu_and_reply(message.chat.id, MENU_BYPASS_LIST, "Меню " + state.selected_file)

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

    def handle_bypass_list_menu(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        if message.text == "📄 Показать список":
            sites = sorted(load_bypass_list(filepath))
            text = "Список пуст" if not sites else "\n".join(sites)
            send_long_message(message.chat.id, text)
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
            set_menu_and_reply(message.chat.id, MENU_TOR, "🔑 Вставьте мосты Tor")
        elif message.text == 'Shadowsocks':
            set_menu_and_reply(message.chat.id, MENU_SHADOWSOCKS, "🔑 Вставьте ключ Shadowsocks")
        elif message.text == 'Vless':
            set_menu_and_reply(message.chat.id, MENU_VLESS, "🔑 Вставьте ключ Vless")
        elif message.text == 'Trojan':
            set_menu_and_reply(message.chat.id, MENU_TROJAN, "🔑 Вставьте ключ Trojan")

    def update_service(chat_id, service_name, config_func, restart_cmd):
        try:
            config_func()
            result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                bot.send_message(chat_id, f'✅ Сервис {service_name} успешно перезапущен')
                return True
            else:
                error_message = result.stderr.strip() or result.stdout.strip() or "Неизвестная ошибка"
                bot.send_message(chat_id, f'❌ Ошибка при перезапуске {service_name}: {error_message}')
                return False
        except Exception:
            return False

    def handle_tor_manually(message):
        success = update_service(message.chat.id, "Tor", 
                                lambda: tor_config(message.text, bot, message.chat.id), 
                                config.services["tor_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести мосты заново", reply_markup=state.current_menu.markup)

    def handle_shadowsocks(message):
        success = update_service(message.chat.id, "Shadowsocks", 
                                lambda: shadowsocks_config(message.text, bot, message.chat.id), 
                                config.services["shadowsocks_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)

    def handle_vless(message):
        success = update_service(message.chat.id, "Vless", 
                                lambda: vless_config(message.text, bot, message.chat.id), 
                                config.services["vless_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)

    def handle_trojan(message):
        success = update_service(message.chat.id, "Trojan", 
                                lambda: trojan_config(message.text, bot, message.chat.id), 
                                config.services["trojan_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)
        
    def toggle_dns_override(chat_id, enable: bool):
        command = config.services["dns_override_on"] if enable else config.services["dns_override_off"]
        status_text = "включен" if enable else "выключен"
        os.system(command)
        os.system(config.services["save_config"])
        bot.send_message(
            chat_id,
            f'{"✅" if enable else "❌"} DNS Override {status_text}!\n⏳ Роутер будет перезапущен!\nЭто займет около 2 минут',
            reply_markup=MENU_SERVICE.markup
        )
        os.system(config.services["router_reboot"])

    def handle_restart(chat_id):
        bot.send_message(chat_id, "⏳ Бот будет перезапущен!\nЭто займет около 15-30 секунд", reply_markup=MENU_SERVICE.markup)
        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        subprocess.Popen([config.paths['script_sh'], '-restart'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    
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
        '🤖 Перезапуск бота': lambda chat_id: handle_restart(chat_id),
        '⛔ Перезапуск роутера': lambda chat_id: (
            bot.send_message(chat_id, "⏳ Роутер будет перезапущен!\nЭто займет около 2 минут", reply_markup=MENU_SERVICE.markup),
            os.system(config.services["router_reboot"])
        ),
        '⁉️ DNS Override': lambda chat_id: set_menu_and_reply(chat_id, MENU_DNS_OVERRIDE),
        '✅ DNS Override ВКЛ': lambda chat_id: toggle_dns_override(chat_id, True),
        '❌ DNS Override ВЫКЛ': lambda chat_id: toggle_dns_override(chat_id, False),
        '🚦 Перезапуск сервисов': lambda chat_id: (
            bot.send_message(chat_id, '⏳ Сервисы будут перезапущены!\nЭто займет около 10-15 секунд'),
            update_service(chat_id, "Shadowsocks", lambda: None, config.services["shadowsocks_restart"]),
            update_service(chat_id, "Tor", lambda: None, config.services["tor_restart"]),
            update_service(chat_id, "Vless", lambda: None, config.services["vless_restart"]),
            update_service(chat_id, "Trojan", lambda: None, config.services["trojan_restart"]),
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

    @bot.message_handler(content_types=['text'])
    def bot_message(message):
        if message.from_user.username not in config.usernames or message.chat.type != 'private':
            bot.send_message(message.chat.id, '⚠️ Вы не являетесь автором канала или это не приватный чат!')
            return

        if message.text in MENU_TRANSITIONS:
            MENU_TRANSITIONS[message.text](message.chat.id)
        elif state.current_menu.level in LEVEL_HANDLERS:
            LEVEL_HANDLERS[state.current_menu.level](message)

    def handle_install(chat_id):
        download_script()
        chat_id = call.message.chat.id
        bot.send_message(chat_id, '⏳ Начинаем утановку, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.send_message(chat_id, line.strip())
        process.wait()
        if process.returncode == 0:
            full_message = "✅ Установка завершена. Теперь нужно настроить роутер и перейти к спискам для разблокировок. Ключи устанавливаются вручную - Ключи и Мосты -> Tor, Vless, Shadowsocks, Trojan.\n\nДля завершения настройки зайдите в меню Сервис -> DNS Override -> ВКЛ. Роутер перезагрузится, это займёт около 2 минут"
            bot.send_message(chat_id, full_message, reply_markup=MENU_MAIN.markup)
        else:
            bot.send_message(chat_id, '❌ Установка завершилась с ошибкой')
    
    def handle_remove(chat_id):
        download_script()
        chat_id = call.message.chat.id
        bot.send_message(chat_id, '⏳ Начинаем удаление, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.send_message(chat_id, line.strip())
        process.wait()
        if process.returncode == 0:
            bot.send_message(chat_id, '✅ Удаление завершено', reply_markup=MENU_SERVICE.markup)
        else:
            bot.send_message(chat_id, '❌ Ошибка при удалении', reply_markup=MENU_SERVICE.markup)

    @bot.callback_query_handler(func=lambda call: call.data == "trigger_update")
    def handle_update(call):
        chat_id = call.message.chat.id
        download_script()
        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        bot.send_message(chat_id, '⏳ Устанавливаются обновления, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-update'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.send_message(chat_id, line.strip())

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
