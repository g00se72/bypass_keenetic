#!/usr/bin/python3
# ВЕРСИЯ СКРИПТА 3.3.7

import os
import sys
import signal
import time
import telebot
import subprocess
from handlers import setup_handlers
from utils import log_error, clean_log, check_restart, signal_handler
import bot_config as config

if not config.token or config.token.strip() == "" or ":" not in config.token or len(config.token) < 10:
    log_error("Ошибка: Токен не указан или имеет неверный формат в bot_config.py")
    sys.exit(1)
    
current_pid = str(os.getpid())
pids_output = subprocess.run(['pgrep', '-f', f'python3 {config.paths["bot_path"]}'], capture_output=True, text=True).stdout.strip()
running_pids = [pid for pid in pids_output.splitlines() if pid and pid != current_pid]
if running_pids:
    log_error(f"Бот уже запущен с PID: {', '.join(running_pids)}")
    sys.exit(1)

bot = telebot.TeleBot(config.token)
restart_count = 0
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    clean_log(config.paths["error_log"])
    
    # Запуск бота и обработчиков
    setup_handlers(bot)
    check_restart(bot)
    
    while restart_count < config.MAX_RESTARTS:
        try:
            bot.infinity_polling()
        except telebot.apihelper.ApiException as err:
            log_error(f"Ошибка Telegram API: {str(err)}")
            restart_count += 1
            time.sleep(config.RESTART_DELAY)
        except Exception as err:
            log_error(f"Неизвестная ошибка: {str(err)}")
            restart_count += 1
            time.sleep(config.RESTART_DELAY)
    log_error("Бот остановлен после достижения максимального количества попыток перезапуска")
