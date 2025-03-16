import os
import time
import bot_config as config
from menu import MENU_CACHE

def download_script():
# Загрузка скрипта с установкой прав
    os.system(f"curl -s -o {config.paths['script_sh']} {config.download_urls['script_sh']}")
    os.chmod(config.paths["script_sh"], 0o0755)

def send_long_message(bot, chat_id, text, parse_mode=None):
# Отправка длинных сообщений по частям
    current_part = ""
    for line in text.split('\n'):
        if len(current_part + '\n' + line) > 4096:
            bot.send_message(chat_id, current_part, parse_mode=parse_mode)
            current_part = line
        else:
            current_part += '\n' + line if current_part else line
    if current_part:
        bot.send_message(chat_id, current_part, parse_mode=parse_mode)

def load_bypass_list(filepath):
# Загрузка списка обхода из файла
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_bypass_list(filepath, sites):
# Сохранение списка обхода в файл
    with open(filepath, 'w') as f:
        f.write('\n'.join(sorted(sites)))

def update_service(bot, chat_id, service_name, config_func, restart_cmd):
# Обновление конфигурации и перезапуск сервиса
    config_func()
    time.sleep(1)
    bot.send_message(chat_id, f'✅ Ключи (мосты) {service_name} обновлены')
    os.system(restart_cmd)
    bot.send_message(chat_id, '🤖 Добро пожаловать в меню!', reply_markup=MENU_CACHE["main"])

def return_to_main_menu(bot, chat_id, level, selected_file):
# Возврат в главное меню
    level = 0
    selected_file = ""
    bot.send_message(chat_id, '🤖 Добро пожаловать в меню!', reply_markup=MENU_CACHE["main"])
    return level, selected_file
