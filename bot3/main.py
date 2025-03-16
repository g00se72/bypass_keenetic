#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.0.0

import telebot
import time
from handlers import setup_handlers
import bot_config as config

bot = telebot.TeleBot(config.token)

# Глобальные переменные
level = 0
selected_file = ""

if __name__ == "__main__":
    setup_handlers(bot, level, selected_file)
    while True:
        try:
            bot.infinity_polling()
        except Exception as err:
            with open(config.paths["error_log"], "a") as fl:
                fl.write(f"{str(err)}\n")
            time.sleep(300)  # Пауза перед перезапуском