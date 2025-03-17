#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.0.2

import os
import sys
import telebot
import time
from handlers import setup_handlers
import bot_config as config

bot = telebot.TeleBot(config.token)

level = 0
restart_count = 0
selected_file = ""
MAX_RESTARTS = 5
PID_FILE = "/opt/var/run/bot.pid"

# Функция для записи PID в файл
def write_pid(PID_FILE):
    try:
        pid = os.getpid()
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                existing_pid = f.read().strip()
                try:
                    os.kill(int(existing_pid), 0)
                    log_error(f"Ошибка: бот с PID {existing_pid} уже запущен.")
                    return False
                except ProcessLookupError:
                    log_error(f"Процесс с PID {existing_pid} не найден, возможно, бот не работает.")
                    os.remove(PID_FILE)

        with open(PID_FILE, "w") as f:
            f.write(str(pid))
        log_error(f"PID {pid} записан в файл {PID_FILE}")
        return True
    except Exception as e:
        log_error(f"Ошибка при записи в файл PID: {e}")
        return False

# Функция для очистки файла PID при завершении работы
def cleanup_pid(PID_FILE):
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            log_error(f"Файл PID удален: {PID_FILE}")
        else:
            log_error(f"PID файл не найден для удаления: {PID_FILE}")
    except Exception as e:
        log_error(f"Ошибка при удалении PID файла: {e}")

# Функция для записи ошибок в файл
def log_error(message):
    try:
        with open(config.paths["error_log"], "a") as fl:
            fl.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Ошибка при записи в log файл: {e}")

if __name__ == "__main__":
    # Проверяем можно ли запустить бот
    if not write_pid(PID_FILE):
        sys.exit(1)

    # Запуск бота и обработчиков
    setup_handlers(bot, level, selected_file)
    try:
        while restart_count < MAX_RESTARTS:
            try:
                bot.infinity_polling()
            except Exception as err:
                log_error(f"Critical Error: {str(err)}")
                restart_count += 1
                time.sleep(60)
        log_error("Бот остановлен после достижения максимального количества попыток перезапуска")
    finally:
        # Удаляем PID файл при завершении работы
        cleanup_pid(PID_FILE)
