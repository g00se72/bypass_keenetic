import subprocess
import requests
import os
import time
from telebot import types
import bot_config as config
from menu import (
    MENU_MAIN, MENU_SERVICE, MENU_KEYS_BRIDGES, MENU_TOR, MENU_VLESS,
    create_backup_menu, BackupState, create_drive_selection_menu, create_delete_archive_menu,
    create_updates_menu, create_install_remove_menu
)
from utils import (
    download_script, vless_config, tor_config, get_available_drives, create_backup_with_params
)

class BotState:
    def __init__(self):
        self.current_menu = MENU_MAIN
        self.selected_file = ""

def setup_handlers(bot):
    state = BotState()
    backup_state = BackupState()
    
    def set_menu_and_reply(chat_id, new_menu, text=None, markup=None):
        state.current_menu = new_menu
        if not text:
            text = new_menu.name
        bot.send_message(chat_id, text, reply_markup=markup if markup else new_menu.markup)

    def handle_keys_bridges_selection(message):
        if message.text == 'Tor':
            set_menu_and_reply(message.chat.id, MENU_TOR, "🔑 Вставьте мосты Tor")
        elif message.text == 'Vless':
            set_menu_and_reply(message.chat.id, MENU_VLESS, "🔑 Вставьте ключ Vless")

    def update_service(chat_id, service_name, config_func, restart_cmd):
        try:
            config_func()
            result = subprocess.run(restart_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                bot.send_message(chat_id, f'✅ Сервис {service_name} успешно перезапущен')
                return True, None
            else:
                error_message = result.stderr.strip() or result.stdout.strip() or "Неизвестная ошибка"
                bot.send_message(chat_id, f'❌ Ошибка при перезапуске {service_name}: {error_message}')
                return False, error_message
        except Exception as e:
            return False, str(e)

    def handle_tor_manually(message):
        success, error = update_service(message.chat.id, "Tor", lambda: tor_config(message.text, bot, message.chat.id), config.services["tor_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести мосты заново", reply_markup=state.current_menu.markup)

    def handle_vless(message):
        success, error = update_service(message.chat.id, "Vless", lambda: vless_config(message.text, bot, message.chat.id), config.services["singbox_restart"] if config.vless_client == "sing-box" else config.services["xray_restart"])
        if success:
            set_menu_and_reply(message.chat.id, MENU_KEYS_BRIDGES)
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)
        
    def handle_restart(chat_id):
        bot.send_message(chat_id, "⏳ Бот будет перезапущен!\nЭто займет около 15-30 секунд", reply_markup=MENU_SERVICE.markup)
        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        subprocess.Popen(config.services['service_script'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

    def handle_backup(chat_id):
        inline_keyboard = create_backup_menu(backup_state)
        bot.send_message(chat_id, "Выберите файлы для бэкапа:", reply_markup=inline_keyboard)

    def handle_install_remove(chat_id):
        inline_keyboard = create_install_remove_menu()
        bot.send_message(chat_id, "Выберите действие:", reply_markup=inline_keyboard)

    def get_local_version():
        version_file = os.path.join(os.path.dirname(__file__), "version.md")
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "N/A"

    def get_remote_version(bot_url):
        response = requests.get(f"{bot_url}/version.md")
        return response.text.strip() if response.status_code == 200 else "N/A"

    def handle_updates(chat_id):
        bot_new_version = get_remote_version(config.bot_url)
        bot_version = get_local_version()        
        service_update_info = f"Установленная версия: {bot_version}\nДоступная на git версия: {bot_new_version}"
        need_update = False
        if bot_version != "N/A" and bot_new_version != "N/A":
            try:
                if tuple(map(int, bot_version.split("."))) < tuple(map(int, bot_new_version.split("."))):
                    need_update = True
            except ValueError:
                service_update_info += "\nОшибка: версии имеют неверный формат"
        else:
            service_update_info += "\nНе удалось проверить обновления"
        inline_keyboard = create_updates_menu(need_update)
        bot.send_message(chat_id, service_update_info, reply_markup=inline_keyboard)
    
    # Словарь переходов и действий
    MENU_TRANSITIONS = {
        '🔙 Назад': lambda chat_id: (
        set_menu_and_reply(chat_id, next(
            (m for m in [MENU_MAIN, MENU_SERVICE, MENU_KEYS_BRIDGES,
                         MENU_TOR, MENU_VLESS]
             if m.level == state.current_menu.back_level), MENU_MAIN))
        ),
        '🔑 Ключи и мосты': lambda chat_id: set_menu_and_reply(chat_id, MENU_KEYS_BRIDGES),
        '⚙️ Сервис': lambda chat_id: set_menu_and_reply(chat_id, MENU_SERVICE),
        '🤖 Перезапуск бота': lambda chat_id: handle_restart(chat_id),
        '🔌 Перезапуск роутера': lambda chat_id: (
            bot.send_message(chat_id, "⏳ Роутер будет перезапущен!\nЭто займет около 2 минут", reply_markup=MENU_SERVICE.markup),
            subprocess.run(["ndmc", "-c", "system reboot"])
        ),
        '🔁 Перезапуск сервисов': lambda chat_id: (
            bot.send_message(chat_id, '⏳ Сервисы будут перезапущены!\nЭто займет около 10-15 секунд'),
            update_service(chat_id, "Tor", lambda: None, config.services["tor_restart"]),
            update_service(chat_id, "Vless", lambda: None, config.services["singbox_restart"] if config.vless_client == "sing-box" else config.services["xray_restart"]),
            bot.send_message(chat_id, '❕ Перезапуск сервисов завершен', reply_markup=MENU_MAIN.markup)
        ),
        '🆕 Обновления': lambda chat_id: handle_updates(chat_id),
        '📲 Установка и удаление': lambda chat_id: handle_install_remove(chat_id),
        '💾 Бэкап': lambda chat_id: handle_backup(chat_id)
    }

    LEVEL_HANDLERS = {
        1: handle_keys_bridges_selection,
        2: handle_tor_manually,
        3: handle_vless
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

    @bot.callback_query_handler(func=lambda call: call.data == "menu_service")
    def handle_backup_return(call):
        state.current_menu = MENU_SERVICE
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MENU_SERVICE.name, reply_markup=MENU_SERVICE.markup)
        backup_state.__init__()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("backup_toggle_"))
    def handle_backup_toggle(call):
        backup_type = call.data.replace("backup_toggle_", "")
        if backup_type == "startup":
            backup_state.startup_config = not backup_state.startup_config
        elif backup_type == "firmware":
            backup_state.firmware = not backup_state.firmware
        elif backup_type == "entware":
            backup_state.entware = not backup_state.entware
        elif backup_type == "custom":
            backup_state.custom_files = not backup_state.custom_files
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_backup_menu(backup_state))
            
    @bot.callback_query_handler(func=lambda call: call.data == "backup_create")
    def handle_backup_create(call):
        drives = get_available_drives()
        if not drives:
            bot.answer_callback_query(call.id, "❌ Нет доступных дисков для бэкапа", show_alert=True)
            return
        msg = bot.edit_message_text("Выберите диск для сохранения бэкапа:", call.message.chat.id, call.message.message_id, reply_markup=create_drive_selection_menu(drives))
        backup_state.selection_msg_id = msg.message_id
                    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backup_drive_"))
    def handle_backup_drive_select(call):
        drive_uuid = call.data.replace("backup_drive_", "")
        drives = get_available_drives()
        selected_drive = next((d for d in drives if d['uuid'] == drive_uuid), None)
        if not selected_drive:
            bot.answer_callback_query(call.id, "❌ Выбранный диск недоступен", show_alert=True)
            return
        backup_state.selected_drive = selected_drive
        bot.edit_message_text(f"☑️ Выбран диск: {selected_drive['label']}\nУдалить архив с диска после создания бэкапа?", call.message.chat.id, backup_state.selection_msg_id, reply_markup=create_delete_archive_menu())

    @bot.callback_query_handler(func=lambda call: call.data in ["backup_delete_yes", "backup_delete_no"])
    def handle_delete_archive_choice(call):
        if call.data == "backup_delete_yes":
            backup_state.delete_archive = True
            choice_text = "Да"
        elif call.data == "backup_delete_no":
            backup_state.delete_archive = False
            choice_text = "Нет"
        bot.edit_message_text(
            f"☑️ Выбран диск: {backup_state.selected_drive['label']}\n☑️ Удалить архив: {choice_text}", call.message.chat.id, backup_state.selection_msg_id)
        progress_msg = bot.send_message(call.message.chat.id, "⏳ Начинаем создание бэкапа, подождите!")
        create_backup_with_params(bot, call.message.chat.id, backup_state, backup_state.selected_drive, progress_msg.message_id)
        backup_state.__init__()

    @bot.callback_query_handler(func=lambda call: call.data == "backup_menu")
    def handle_backup_menu_return(call):
        bot.edit_message_text("Выберите файлы для бэкапа:", call.message.chat.id, call.message.message_id, reply_markup=create_backup_menu(backup_state))
        
    @bot.callback_query_handler(func=lambda call: call.data == "trigger_update")
    def handle_update(call):
        chat_id = call.message.chat.id
        download_script()
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, '⏳ Устанавливаются обновления, подождите!')
        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        process = subprocess.Popen([config.paths['script_sh'], '-update'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == "install")
    def handle_install_callback(call):
        chat_id = call.message.chat.id
        download_script()
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, '⏳ Начинаем установку, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)
        process.wait()
        if process.returncode == 0:
            bot.send_message(chat_id, '✅ Установка завершена', reply_markup=MENU_MAIN.markup)
        else:
            bot.send_message(chat_id, '❌ Установка завершилась с ошибкой', reply_markup=MENU_MAIN.markup)

    @bot.callback_query_handler(func=lambda call: call.data == "remove")
    def handle_remove_callback(call):
        chat_id = call.message.chat.id
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        download_script()
        msg = bot.send_message(chat_id, '⏳ Начинаем удаление, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)
        process.wait()
        if process.returncode == 0:
            bot.send_message(chat_id, '✅ Удаление завершено', reply_markup=MENU_MAIN.markup)
        else:
            bot.send_message(chat_id, '❌ Ошибка при удалении', reply_markup=MENU_MAIN.markup)

    @bot.callback_query_handler(func=lambda call: call.data == "menu_main")
    def handle_back_to_main(call):
        state.current_menu = MENU_MAIN
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MENU_MAIN.name, reply_markup=MENU_MAIN.markup)
