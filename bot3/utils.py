import os
import time
import subprocess
import bot_config as config
from menu import MENU_CACHE

def download_script():
    # Загрузка скрипта с установкой прав
    subprocess.run(["curl", "-s", "-o", config.paths["script_sh"], config.download_urls["script_sh"]])
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
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def save_bypass_list(filepath, sites):
# Сохранение списка обхода в файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(sites)))

def update_service(bot, chat_id, service_name, config_func, restart_cmd):
# Обновление конфигурации и перезапуск сервиса без отправки клавиатуры
    config_func()
    result = subprocess.run(restart_cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        bot.send_message(chat_id, f'✅ Сервис {service_name} успешно перезапущен')
    else:
        error_message = result.stderr.decode().strip() or "Неизвестная ошибка"
        bot.send_message(chat_id, f'❌ Ошибка при перезапуске {service_name}: {error_message}')

def return_to_main_menu(bot, chat_id, level, selected_file):
# Возврат в главное меню
    level, selected_file = 0, ""
    bot.send_message(chat_id, '🤖 Добро пожаловать в меню!', reply_markup=MENU_CACHE["main"])
    return level, selected_file

def toggle_dns_override(bot, chat_id, enable: bool):
# Включает или выключает DNS Override
    command = config.services["dns_override_on"] if enable else config.services["dns_override_off"]
    status_text = "включен" if enable else "выключен"
    os.system(command)
    os.system(config.services["save_config"])
    bot.send_message(
        chat_id,
        f'{"✅" if enable else "❌"} DNS Override {status_text}!\n⏳ Роутер будет перезапущен!\nЭто займет около 2 минут',
        reply_markup=MENU_CACHE["service"]
    )
    os.system(config.services["router_reboot"])

def log_error(message):
# Функция для записи ошибок в файл
    try:
        with open(config.paths["error_log"], "a") as fl:
            fl.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Ошибка при записи в log файл: {e}")

# Функция для записи PID в файл
def write_pid(pid_file):
    try:
        pid = os.getpid()
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                existing_pid = f.read().strip()
                try:
                    os.kill(int(existing_pid), 0)
                    log_error(f"Ошибка: бот с PID {existing_pid} уже запущен")
                    return False
                except ProcessLookupError:
                    log_error(f"Процесс с PID {existing_pid} не найден, возможно, удаляем старый PID-файл и продолжаем")
                    os.remove(pid_file)

        with open(pid_file, "w") as f:
            f.write(str(pid))
        log_error(f"PID {pid} записан в файл {pid_file}")
        return True
    except Exception as e:
        log_error(f"Ошибка при записи в файл PID: {e}")
        return False

# Функция для очистки файла PID при завершении работы
def cleanup_pid(pid_file):
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            log_error(f"Файл PID удален: {pid_file}")
    except Exception as e:
        log_error(f"Ошибка при удалении PID файла: {e}")
