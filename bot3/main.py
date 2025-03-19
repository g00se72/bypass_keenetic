#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.0.3

import os
import sys
import time
import telebot
from handlers import setup_handlers
from utils import log_error, write_pid, cleanup_pid
import bot_config as config

bot = telebot.TeleBot(config.token)

level = 0
restart_count = 0
selected_file = ""


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
