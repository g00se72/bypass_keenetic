from telebot import types
import bot_config as config

class Menu:
    def __init__(self, name, markup, level, back_level=None):
        self.name = name
        self.markup = markup
        self.level = level
        self.back_level = back_level

class BackupState:
    def __init__(self):
        self.startup_config = False
        self.firmware = False
        self.entware = False
        self.custom_files = False
        self.selected_drive = None
        self.delete_archive = False

    def get_selected_count(self):
        return sum([self.startup_config, self.firmware, self.entware, self.custom_files])

    def get_selected_types(self):
        types = []
        if self.startup_config: types.append("Конфигурация")
        if self.firmware: types.append("Прошивка")
        if self.entware: types.append("Entware")
        if self.custom_files: types.append("Другие файлы")
        return types

def create_menu(buttons, resize_keyboard=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)
    for row in buttons:
        markup.add(*row)
    return markup

def create_button(text, callback_data):
    return types.InlineKeyboardButton(text, callback_data=callback_data)

def create_backup_menu(backup_state):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button(f"{'✅' if backup_state.startup_config else '✖️'} Конфигурация", "backup_toggle_startup"),
        create_button(f"{'✅' if backup_state.firmware else '✖️'} Прошивка", "backup_toggle_firmware")
    )
    markup.add(
        create_button(f"{'✅' if backup_state.entware else '✖️'} Entware", "backup_toggle_entware"),
        create_button(f"{'✅' if backup_state.custom_files else '✖️'} Другие файлы", "backup_toggle_custom")
    )
    if backup_state.get_selected_count() > 0:
        markup.add(create_button("💾 Создать бэкап", "backup_create"))
    markup.add(create_button("🔙 Назад", "menu_service"))
    return markup

def create_drive_selection_menu(drives):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for drive in drives:
        button_text = f"💽 {drive['label']} ({drive['size']} GB свободно)"
        markup.add(create_button(button_text, f"backup_drive_{drive['uuid']}"))
    markup.add(create_button("🔙 Назад", "backup_menu"))
    return markup

def create_delete_archive_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button("Да", "backup_delete_yes"),
        create_button("Нет", "backup_delete_no")
    )
    markup.add(create_button("🔙 Назад", "backup_create"))
    return markup
    
def create_updates_menu(need_update):
    markup = types.InlineKeyboardMarkup()
    if need_update:
        markup.add(create_button("🆕 Обновить", "trigger_update"))
    markup.add(create_button("🔙 Назад", "menu_service"))
    return markup

def create_install_remove_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button("📲 Установка", "install"),
        create_button("🗑 Удаление", "remove")
    )
    markup.add(create_button("🔙 Назад", "menu_main"))
    return markup

MENU_MAIN = Menu("🤖 Добро пожаловать в меню!", create_menu([
    ["🔑 Ключи и мосты", "⚙️ Сервис"],
    ["📲 Установка и удаление"]
]), 0)

MENU_KEYS_BRIDGES = Menu("🔑 Ключи и мосты", create_menu([
    ["Tor", "Vless"],
    ["🔙 Назад"]
]), 1, 0)

MENU_TOR = Menu("Tor", create_menu([["🔙 Назад"]]), 2, 1)
MENU_VLESS = Menu("Vless", create_menu([["🔙 Назад"]]), 3, 1)

MENU_SERVICE = Menu("⚙️ Сервисное меню!", create_menu([
    ["🤖 Перезапуск бота", "🔌 Перезапуск роутера", "🔁 Перезапуск сервисов"],
    ["🆕 Обновления", "💾 Бэкап"],
    ["🔙 Назад"]
]), 2, 0)
