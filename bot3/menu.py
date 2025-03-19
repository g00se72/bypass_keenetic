from telebot import types
import bot_config as config
import os

class Menu:
    def __init__(self, name, markup, level, back_level=None):
        self.name = name
        self.markup = markup
        self.level = level
        self.back_level = back_level

def create_menu(buttons, resize_keyboard=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)
    for row in buttons:
        markup.add(*row)
    return markup

# Определение всех меню как объектов класса Menu
MENU_MAIN = Menu("🤖 Добро пожаловать в меню!", create_menu([
    ["🔑 Ключи и мосты", "📑 Списки обхода"],
    ["📲 Установка и удаление", "⚙️ Сервис"],
    ["💡 Информация"]
]), 0)

MENU_BYPASS_FILES = Menu("📑 Списки обхода", None, 1, 0)

MENU_BYPASS_LIST = Menu("Bypass List", create_menu([
    ["📄 Показать список", "➕ Добавить в список", "➖ Удалить из списка"],
    ["🔙 Назад"]
]), 2, 1)

MENU_ADD_BYPASS = Menu("➕ Добавить в список", create_menu([["🔙 Назад"]]), 3, 2)
MENU_REMOVE_BYPASS = Menu("➖ Удалить из списка", create_menu([["🔙 Назад"]]), 4, 2)

MENU_KEYS_BRIDGES = Menu("🔑 Ключи и мосты", create_menu([
    ["Tor", "Vless", "Trojan", "Shadowsocks"],
    ["🔙 Назад"]
]), 5, 0)

MENU_TOR = Menu("Tor", create_menu([["🔙 Назад"]]), 8, 5)
MENU_SHADOWSOCKS = Menu("Shadowsocks", create_menu([["🔙 Назад"]]), 9, 5)
MENU_VLESS = Menu("Vless", create_menu([["🔙 Назад"]]), 10, 5)
MENU_TROJAN = Menu("Trojan", create_menu([["🔙 Назад"]]), 11, 5)

MENU_SERVICE = Menu("⚙️ Сервисное меню!", create_menu([
    ["🤖 Перезапуск бота", "⛔ Перезапуск роутера", "🚦 Перезапуск сервисов"],
    ["⁉️ DNS Override", "🔄 Обновления"],
    ["🔙 Назад"]
]), 6, 0)

MENU_DNS_OVERRIDE = Menu("⁉️ DNS Override", create_menu([
    ["✅ DNS Override ВКЛ", "❌ DNS Override ВЫКЛ"],
    ["🔙 Назад"]
]), 7, 6)

MENU_INSTALL_REMOVE = Menu("📲 Установка и удаление", create_menu([
    ["📲 Установка", "🗑 Удаление"],
    ["🔙 Назад"]
]), 12, 0)

def create_bypass_files_menu():
    dirname = config.paths["unblock_dir"]
    buttons = []
    if os.path.exists(dirname) and os.listdir(dirname):
        file_buttons = [fln.replace(".txt", "") for fln in os.listdir(dirname)]
        buttons.append(file_buttons)
    else:
        buttons.append(["Нет доступных файлов"])
    buttons.append(["🔙 Назад"])
    MENU_BYPASS_FILES.markup = create_menu(buttons)
    return MENU_BYPASS_FILES.markup
