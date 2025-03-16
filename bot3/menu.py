from telebot import types
import bot_config as config
import os

MENU_CACHE = {}

def create_menu(buttons, resize_keyboard=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)
    for row in buttons:
        markup.row(*row)
    return markup

def init_menus():
    MENU_CACHE["main"] = create_main_menu()
    MENU_CACHE["service"] = create_service_menu()
    MENU_CACHE["install_remove"] = create_install_remove_menu()
    MENU_CACHE["keys_bridges"] = create_keys_bridges_menu()
    MENU_CACHE["bypass_list"] = create_bypass_list_menu()
    MENU_CACHE["back"] = create_back_menu()
    MENU_CACHE["dns_override"] = create_dns_override_menu()

def create_main_menu():
    buttons = [
        ["🔑 Ключи и мосты", "📑 Списки обхода"],
        ["📲 Установка и удаление", "⚙️ Сервис"],
        ["💡 Информация"]
    ]
    return create_menu(buttons)

def create_service_menu():
    buttons = [
        ["🤖 Перезапуск бота", "⛔ Перезапуск роутера", "🚦 Перезапуск сервисов"],
        ["⁉️ DNS Override", "🔄 Обновления"],
        ["🔙 Назад"]
    ]
    return create_menu(buttons)

def create_install_remove_menu():
    buttons = [
        ["📲 Установка", "🗑 Удаление"],
        ["🔙 Назад"]
    ]
    return create_menu(buttons)

def create_keys_bridges_menu():
    buttons = [
        ["Shadowsocks", "Tor"],
        ["Vless", "Trojan"],
        ["🔙 Назад"]
    ]
    return create_menu(buttons)

def create_bypass_list_menu():
    buttons = [
        ["📄 Показать список", "➕ Добавить в список", "➖ Удалить из списка"],
        ["🔙 Назад"]
    ]
    return create_menu(buttons)

def create_back_menu():
    buttons = [["🔙 Назад"]]
    return create_menu(buttons)

def create_dns_override_menu():
    buttons = [
        ["✅ DNS Override ВКЛ", "❌ DNS Override ВЫКЛ"],
        ["🔙 Назад"]
    ]
    return create_menu(buttons)

def create_bypass_files_menu():
    dirname = config.paths["unblock_dir"]
    buttons = []
    if os.path.exists(dirname):
        dirfiles = os.listdir(dirname)
        file_buttons = [fln.replace(".txt", "") for fln in dirfiles]
        for i in range(0, len(file_buttons), 3):
            buttons.append(file_buttons[i:i + 3])
    buttons.append(["🔙 Назад"])
    return create_menu(buttons)

init_menus()