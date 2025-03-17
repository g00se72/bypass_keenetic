#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.0.1

import telebot
import time
from handlers import setup_handlers
import bot_config as config

bot = telebot.TeleBot(config.token)

level = 0
restart_count = 0
selected_file = ""
MAX_RESTARTS = 5

if __name__ == "__main__":
    setup_handlers(bot, level, selected_file)

    while restart_count < MAX_RESTARTS:
        try:
            bot.infinity_polling()
        except Exception as err:
            with open(config.paths["error_log"], "a") as fl:
                fl.write(f"Critical Error: {str(err)}\n")
            restart_count += 1
            time.sleep(60)
    
    with open(config.paths["error_log"], "a") as fl:
        fl.write("Бот остановлен после достижения максимального количества попыток перезапуска\n")
