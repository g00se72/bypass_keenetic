import os
import time
import subprocess
import json
import re
from urllib.parse import urlparse, parse_qs
import base64
import bot_config as config

def download_script():
    # Загрузка скрипта с установкой прав
    subprocess.run(["curl", "-s", "-o", config.paths["script_sh"], config.download_urls["script_sh"]])
    os.chmod(config.paths["script_sh"], 0o0755)

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

def log_error(message):
    # Функция для записи ошибок в файл
    try:
        with open(config.paths["error_log"], "a") as fl:
            fl.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Ошибка при записи в log файл: {e}")

def write_pid(pid_file):
    # Функция для записи PID в файл
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
                    log_error(f"Процесс с PID {existing_pid} не найден, удаляем старый PID-файл и продолжаем")
                    os.remove(pid_file)

        with open(pid_file, "w") as f:
            f.write(str(pid))
        log_error(f"PID {pid} записан в файл {pid_file}")
        return True
    except Exception as e:
        log_error(f"Ошибка при записи в файл PID: {e}")
        return False

def cleanup_pid(pid_file):
    # Функция для очистки файла PID при завершении работы
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            log_error(f"Файл PID удален: {pid_file}")
    except Exception as e:
        log_error(f"Ошибка при удалении PID файла: {e}")

class ConfigWriter:
    @staticmethod
    def write_config(file_path, config_data, format='json'):
        with open(file_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                f.write(config_data)
            else:
                f.write(config_data)

def parse_vless_key(key, bot=None, chat_id=None):
    try:
        if not key.startswith("vless://"):
            raise ValueError("Ключ должен начинаться с 'vless://'")
        url = key[6:]
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        if not parsed_url.hostname or not parsed_url.username:
            raise ValueError("Отсутствует адрес сервера или ID пользователя")
        return {
            'address': parsed_url.hostname,
            'port': parsed_url.port or 443,
            'id': parsed_url.username,
            'security': params.get('security', [''])[0],
            'encryption': params.get('encryption', ['none'])[0],
            'pbk': params.get('pbk', [''])[0],
            'fp': params.get('fp', [''])[0],
            'spx': params.get('spx', ['/'])[0],
            'flow': params.get('flow', ['xtls-rprx-vision'])[0],
            'sni': params.get('sni', [''])[0],
            'sid': params.get('sid', [''])[0]
        }
    except Exception as e:
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка в ключе Vless: {str(e)}")
        raise

def parse_trojan_key(key, bot=None, chat_id=None):
    try:
        if not key.startswith("trojan://"):
            raise ValueError("Ключ должен начинаться с 'trojan://'")
        key = key.split('//')[1]
        pw = key.split('@')[0]
        if not pw:
            raise ValueError("Отсутствует пароль")
        key = key.replace(pw + "@", "", 1)
        host = key.split(':')[0]
        port = key.split(':')[1].split('?')[0].split('#')[0]
        if not host or not port.isdigit():
            raise ValueError("Некорректный адрес сервера или порт")
        return {'pw': pw, 'host': host, 'port': int(port)}
    except Exception as e:
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка в ключе Trojan: {str(e)}")
        raise

def parse_shadowsocks_key(key, bot=None, chat_id=None):
    try:
        if not key.startswith("ss://"):
            raise ValueError("Ключ должен начинаться с 'ss://'")
        encodedkey = key.split('//')[1].split('@')[0] + '=='
        decoded = base64.b64decode(encodedkey)
        method = str(decoded.split(b':')[0])[2:]
        password = str(decoded[2:].split(b':')[1])[:-1]
        server = key.split('@')[1].split('/')[0].split(':')[0]
        port = key.split('@')[1].split('/')[0].split(':')[1].split('#')[0]
        if not server or not port.isdigit() or not method or not password:
            raise ValueError("Некорректные данные сервера, порта, метода или пароля")
        return {'server': server, 'port': int(port), 'password': password, 'method': method}
    except Exception as e:
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка в ключе Shadowsocks: {str(e)}")
        raise

def vless_config(key, bot=None, chat_id=None):
    try:
        params = parse_vless_key(key, bot, chat_id)
        with open(os.path.join(config.paths["templates_dir"], "vless_template.json"), 'r', encoding='utf-8') as f:
            template = f.read()
        config_data = template.replace("{{localportvless}}", str(config.localportvless))
        for key, value in params.items():
            config_data = config_data.replace("{{" + key + "}}", str(value))
        ConfigWriter.write_config(config.paths["vless_config"], config_data)
    except Exception as e:
        raise
        
def trojan_config(key, bot=None, chat_id=None):
    try:
        params = parse_trojan_key(key, bot, chat_id)
        with open(os.path.join(config.paths["templates_dir"], "trojan_template.json"), 'r', encoding='utf-8') as f:
            template = f.read()
        config_data = template.replace("{{localporttrojan}}", str(config.localporttrojan))
        config_data = config_data.replace("{{host}}", params['host'])
        config_data = config_data.replace("{{port}}", str(params['port']))
        config_data = config_data.replace("{{pw}}", params['pw'])
        ConfigWriter.write_config(config.paths["trojan_config"], config_data)
    except Exception as e:
        raise

def shadowsocks_config(key, bot=None, chat_id=None):
    try:
        params = parse_shadowsocks_key(key, bot, chat_id)
        with open(os.path.join(config.paths["templates_dir"], "shadowsocks_template.json"), 'r', encoding='utf-8') as f:
            template = f.read()
        config_data = template.replace("{{localportsh}}", str(config.localportsh))
        config_data = config_data.replace("{{server}}", params['server'])
        config_data = config_data.replace("{{port}}", str(params['port']))
        config_data = config_data.replace("{{password}}", params['password'])
        config_data = config_data.replace("{{method}}", params['method'])
        ConfigWriter.write_config(config.paths["shadowsocks_config"], config_data)
    except Exception as e:
        raise

def tor_config(bridges, bot=None, chat_id=None):
    try:
        bridge_lines = bridges.strip().split('\n')
        valid_transports = {"obfs4", "obfs3", "meek", "scramblesuit"}
        ip_port_pattern = re.compile(r"^(?:(?:\d{1,3}\.){3}\d{1,3}|\[[0-9a-fA-F:]*\]):\d{1,5}$")
        for line in bridge_lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                raise ValueError(f"Некорректный мост: '{line}'")
            if parts[0] in valid_transports:
                if len(parts) < 2:
                    raise ValueError(f"Указан транспорт '{parts[0]}', но нет IP:порт в '{line}'")
                ip_port = parts[1]
            else:
                ip_port = parts[0]
            if not ip_port_pattern.match(ip_port):
                raise ValueError(f"Некорректный формат IP:порт в '{line}'")

        with open(os.path.join(config.paths["templates_dir"], "tor_template.torrc"), 'r', encoding='utf-8') as f:
            config_data = f.read()
        config_data = config_data.replace("{{localporttor}}", str(config.localporttor))
        config_data = config_data.replace("{{dnsporttor}}", str(config.dnsporttor))
        config_data = config_data.replace("{{bridges}}", bridges.replace("obfs4", "Bridge obfs4"))
        ConfigWriter.write_config(config.paths["tor_config"], config_data, format='text')
    except Exception as e:
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка в мостах Tor: {str(e)}")
        raise
