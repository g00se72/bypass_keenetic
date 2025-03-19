#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.1.0

import sys
import time
import telebot
from handlers import setup_handlers
from utils import log_error, write_pid, cleanup_pid
import bot_config as config

restart_count = 0

if not config.token or config.token.strip() == "" or ":" not in config.token or len(config.token) < 10:
    log_error("Ошибка: Токен не указан или имеет неверный формат в bot_config.py")
    sys.exit(1)

bot = telebot.TeleBot(config.token)

if __name__ == "__main__":
    # Проверяем можно ли запустить бот
    if not write_pid(config.paths["pid_path"]):
        sys.exit(1)

    # Запуск бота и обработчиков
    log_error("Запускаем бота...")
    setup_handlers(bot)
    try:
        while restart_count < config.MAX_RESTARTS:
            try:
                bot.infinity_polling()
            except Exception as err:
                log_error(f"Critical Error: {str(err)}")
                restart_count += 1
                time.sleep(config.RESTART_DELAY)
        log_error("Бот остановлен после достижения максимального количества попыток перезапуска")
    except KeyboardInterrupt:
        log_error("Бот остановлен пользователем")
    finally:
        # Удаляем PID-файл при завершении работы
        cleanup_pid(config.paths["pid_path"])
