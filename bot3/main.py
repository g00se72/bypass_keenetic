#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.0.3

import os
import sys
import time
import telebot
from handlers import setup_handlers
from utils import log_error
import bot_config as config

bot = telebot.TeleBot(config.token)

level = 0
restart_count = 0
selected_file = ""

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
                    log_error(f"Процесс с PID {existing_pid} не найден, возможно, бот не работает")
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
        else:
            log_error(f"PID файл не найден для удаления: {pid_file}")
    except Exception as e:
        log_error(f"Ошибка при удалении PID файла: {e}")

if __name__ == "__main__":
    # Проверяем можно ли запустить бот
    if not write_pid(config.paths["bot_pid_path"]):
        sys.exit(1)

    # Запуск бота и обработчиков
    setup_handlers(bot, level, selected_file)
    try:
        while restart_count < config.MAX_RESTARTS:
            try:
                bot.infinity_polling()
            except Exception as err:
                log_error(f"Critical Error: {str(err)}")
                restart_count += 1
                time.sleep(config.RESTART_DELAY)
        log_error("Бот остановлен после достижения максимального количества попыток перезапуска")
    finally:
        # Удаляем PID файл при завершении работы
        cleanup_pid(config.paths["bot_pid_path"])
