import os
import signal
import time
import subprocess
import json
import re
import tarfile
from urllib.parse import urlparse, parse_qs
import base64
import bot_config as config

def signal_handler(sig, frame):
    # Обрабатывает сигналы завершения Ctrl+C и kill -TERM
    log_error(f"Бот остановлен сигналом {signal.Signals(sig).name}")
    raise SystemExit

def clean_log(log_file):
    # Очистка лога
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
        return

    file_size = os.path.getsize(log_file)
    max_size = 524288
    if file_size > max_size:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        with open(log_file, 'w') as f:
            f.writelines(lines[-50:])

def log_error(message):
    # Функция для записи ошибок в файл
    with open(config.paths["error_log"], "a", encoding='utf-8') as fl:
        fl.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def download_script():
    # Загрузка скрипта с установкой прав
    subprocess.run(["curl", "-s", "-o", config.paths["script_sh"], f"{config.bot_url}/script.sh"])
    os.chmod(config.paths["script_sh"], 0o0755)

def load_bypass_list(filepath):
    # Загрузка списка обхода из файла
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def save_bypass_list(filepath, sites):
    # Сохранение списка обхода в файл
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(sites)))
    except Exception as e:
        log_error(f"Ошибка при сохранении списка обхода: {str(e)}")
        raise

def check_restart(bot):
    # Проверка перезапуска бота
    chat_id_path = config.paths["chat_id_path"]
    if os.path.exists(chat_id_path):
        with open(chat_id_path, 'r') as f:
            chat_id = int(f.read().strip())
        try:
            bot.send_message(chat_id, '✅ Бот перезапущен')
        except Exception as e:
            log_error(f"Ошибка при отправке сообщения после перезапуска: {str(e)}")
        os.remove(chat_id_path)

class ConfigWriter:
    @staticmethod
    def write_config(file_path, config_data, format='json'):
    # Сохранить как json или как текст
        with open(file_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(json.loads(config_data), f, ensure_ascii=False, indent=2)
            else:
                f.write(config_data)

def notify_on_error():
    def decorator(func):
    # Декоратор для обработки ошибок
        def wrapper(key, bot=None, chat_id=None, *args, **kwargs):
            try:
                return func(key, bot, chat_id, *args, **kwargs)
            except Exception as e:
                if bot and chat_id:
                    if func.__name__ == "tor_config":
                        bot.send_message(chat_id, f"❌ Ошибка в мостах Tor: {str(e)}")
                    else:
                        protocol = func.__name__.split('_')[1].capitalize()
                        bot.send_message(chat_id, f"❌ Ошибка в ключе {protocol}: {str(e)}")
                raise
        return wrapper
    return decorator

@notify_on_error()
def parse_vless_key(key, bot=None, chat_id=None):
    # Парсинг vless
    vless_pattern = re.compile(
        r"^vless://[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        r"@(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[0-9a-fA-F:]*\]|[a-zA-Z0-9.-]+)"
        r":\d{1,5}(?:\?.*)?(?:#.*)?$"
    )
    if not vless_pattern.match(key):
        raise ValueError("Неверный формат ключа VLESS. Ожидается: vless://<UUID>@<IP>:<порт>?параметры#имя")

    url = key[6:]
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    if not parsed_url.hostname or not parsed_url.username:
        raise ValueError("Отсутствует адрес сервера или ID пользователя")
    
    port = parsed_url.port or 443
    if not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535, получено: {port}")

    return {
        'address': parsed_url.hostname,
        'port': port,
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

@notify_on_error()
def parse_trojan_key(key, bot=None, chat_id=None):
    # Парсинг trojan
    trojan_pattern = re.compile(
        r"^trojan://[^@]+@(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[0-9a-fA-F:]*\]|[a-zA-Z0-9.-]+)"
        r":\d{1,5}(?:\?.*)?(?:#.*)?$"
    )
    if not trojan_pattern.match(key):
        raise ValueError("Неверный формат ключа Trojan. Ожидается: trojan://<пароль>@<IP>:<порт>?параметры#имя")

    key = key.split('//')[1]
    pw = key.split('@')[0]
    if not pw:
        raise ValueError("Отсутствует пароль")
    key = key.replace(pw + "@", "", 1)
    host = key.split(':')[0]
    port = key.split(':')[1].split('?')[0].split('#')[0]
    if not host or not port.isdigit():
        raise ValueError("Некорректный адрес сервера или порт")
    
    port_num = int(port)
    if not (1 <= port_num <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535, получено: {port}")

    return {'pw': pw, 'host': host, 'port': port_num}

@notify_on_error()
def parse_shadowsocks_key(key, bot=None, chat_id=None):
    # Парсинг ss
    ss_pattern = re.compile(
        r"^ss://[A-Za-z0-9+/=]+@(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[0-9a-fA-F:]*\]|[a-zA-Z0-9.-]+)"
        r":\d{1,5}(?:[/?#].*)?$"
    )
    if not ss_pattern.match(key):
        raise ValueError("Неверный формат ключа Shadowsocks. Ожидается: ss://<base64(метод:пароль)>@<IP>:<порт>#имя")

    encodedkey = key.split('//')[1].split('@')[0] + '=='
    decoded = base64.b64decode(encodedkey).decode('utf-8') 
    method, password = decoded.split(':', 1)
    server_port = key.split('@')[1].split('#')[0].split('?')[0].split('/')[0]
    server, port = server_port.split(':')
    if not server or not port.isdigit() or not method or not password:
        raise ValueError("Некорректные данные сервера, порта, метода или пароля")
    
    port_num = int(port)
    if not (1 <= port_num <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535, получено: {port}")

    return {'server': server, 'port': port_num, 'password': password, 'method': method}

def generate_config(key, template_file, config_path, replacements, parse_func, bot=None, chat_id=None):
    # Создание конфигурационных файлов
    params = parse_func(key, bot, chat_id)
    with open(os.path.join(config.paths["templates_dir"], template_file), 'r', encoding='utf-8') as f:
        template = f.read()
    config_data = template
    for key, value in replacements.items():
        config_data = config_data.replace("{{" + key + "}}", str(value))
    for key, value in params.items():
        config_data = config_data.replace("{{" + key + "}}", str(value))
    ConfigWriter.write_config(config_path, config_data)

def vless_config(key, bot=None, chat_id=None):
    generate_config(
        key=key,
        template_file="vless_template.json",
        config_path=config.paths["vless_config"],
        replacements={"localportvless": config.localportvless},
        parse_func=parse_vless_key,
        bot=bot,
        chat_id=chat_id
    )

def trojan_config(key, bot=None, chat_id=None):
    generate_config(
        key=key,
        template_file="trojan_template.json",
        config_path=config.paths["trojan_config"],
        replacements={"localporttrojan": config.localporttrojan},
        parse_func=parse_trojan_key,
        bot=bot,
        chat_id=chat_id
    )

def shadowsocks_config(key, bot=None, chat_id=None):
    generate_config(
        key=key,
        template_file="shadowsocks_template.json",
        config_path=config.paths["shadowsocks_config"],
        replacements={"localportsh": config.localportsh},
        parse_func=parse_shadowsocks_key,
        bot=bot,
        chat_id=chat_id
    )

@notify_on_error()
def tor_config(bridges, bot=None, chat_id=None):
    bridge_lines = bridges.strip().split('\n')
    valid_transports = {"obfs4", "webtunnel"}
    ip_port_pattern = re.compile(r"^(?:(?:\d{1,3}\.){3}\d{1,3}|\[[0-9a-fA-F:]*\]):\d{1,5}$")
    url_pattern = re.compile(r"^https?://[^\s/$.?#].\S*$")
    
    for line in bridge_lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            raise ValueError(f"Некорректный мост: '{line}'")
            
        transport_type = parts[0] if parts[0] in valid_transports else None
        
        if transport_type:
            if len(parts) < 2:
                raise ValueError(f"Указан транспорт '{parts[0]}', но нет IP:порт или параметров в '{line}'")
            bridge_data = parts[1]
        else:
            bridge_data = parts[0]
        
        if transport_type == "webtunnel":
            if not ip_port_pattern.match(bridge_data):
                raise ValueError(f"Некорректный формат IP:порт в '{line}'")
            url_match = next((part[4:] for part in parts if part.startswith("url=")), None)
            
            if not url_match:
                raise ValueError(f"Отсутствует параметр url= в webtunnel мосту: '{line}'")
            if not url_pattern.match(url_match):
                raise ValueError(f"Некорректный формат URL в webtunnel: '{url_match}' в строке '{line}'")
        else:
            if not ip_port_pattern.match(bridge_data):
                raise ValueError(f"Некорректный формат IP:порт в '{line}'")

    with open(os.path.join(config.paths["templates_dir"], "tor_template.torrc"), 'r', encoding='utf-8') as f:
        config_data = f.read()
        config_data = config_data.replace("{{localporttor}}", str(config.localporttor))
        config_data = config_data.replace("{{dnsporttor}}", str(config.dnsporttor))
        config_data = config_data.replace("{{bridges}}", bridges.replace("obfs4", "Bridge obfs4").replace("webtunnel", "Bridge webtunnel"))
    ConfigWriter.write_config(config.paths["tor_config"], config_data, format='text')

def create_backup_with_params(bot, chat_id, backup_state, selected_drive, progress_msg_id):
    # Функция создания бекапа
    args = [config.paths["script_bu"]]
    max_size = config.backup_settings.get("MAX_SIZE_MB") * 1024 * 1024
    args.extend([
        f"LOG_FILE={config.backup_settings['LOG_FILE']}",
        f"SELECTED_DRIVE={selected_drive['path']}",
        f"BACKUP_STARTUP_CONFIG={str(backup_state.startup_config).lower()}",
        f"BACKUP_FIRMWARE={str(backup_state.firmware).lower()}",
        f"BACKUP_ENTWARE={str(backup_state.entware).lower()}",
        f"BACKUP_CUSTOM_FILES={str(backup_state.custom_files).lower()}"
    ])
    if backup_state.custom_files and 'CUSTOM_BACKUP_PATHS' in config.backup_settings:
        args.append(f"CUSTOM_BACKUP_PATHS={config.backup_settings['CUSTOM_BACKUP_PATHS']}")

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
    final_result = None

    for line in process.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("type") == "progress":
                bot.edit_message_text(f"⏳ {data['message']}", chat_id, progress_msg_id)
            elif "status" in data:
                final_result = data
        except json.JSONDecodeError:
            pass

    process.wait()

    if final_result and final_result["status"] == "success":
        archive_path = final_result["archive_path"]
        if os.path.exists(archive_path):
            archive_size = os.path.getsize(archive_path)
            if archive_size <= max_size:
                bot.edit_message_text("✅ Бэкап создан, отправляю файл...", chat_id, progress_msg_id)
                with open(archive_path, "rb") as f:
                    bot.send_document(chat_id, f, caption=f"✅ Бэкап создан:\n{', '.join(backup_state.get_selected_types())}")
                bot.edit_message_text(f"✅ Бэкап успешно завершен: {', '.join(backup_state.get_selected_types())}", chat_id, progress_msg_id)
            else:
                bot.edit_message_text(f"❕ Архив слишком большой ({archive_size // 1024 // 1024} MB), разбиваю на части...", chat_id, progress_msg_id)
                split_prefix = f"{archive_path}_part_"
                try:
                    subprocess.run(["split", "-b", str(max_size), archive_path, split_prefix], check=True)
                    part_files = [f for f in os.listdir(os.path.dirname(archive_path)) if f.startswith(os.path.basename(split_prefix))]
                    for part_file in sorted(part_files):
                        part_path = os.path.join(os.path.dirname(archive_path), part_file)
                        with open(part_path, "rb") as f:
                            bot.send_document(chat_id, f, caption=f"⏳ Часть бэкапа ({part_file})")
                        os.remove(part_path)
                    bot.edit_message_text(f"✅ Бэкап создан и разбит на части:\n{', '.join(backup_state.get_selected_types())}\n"
                                        f"Для восстановления объедините части:\n"
                                        f"cat {os.path.basename(archive_path)}_part_* > {os.path.basename(archive_path)}", 
                                        chat_id, progress_msg_id)
                except subprocess.CalledProcessError as e:
                    log_error(f"Ошибка при разбиении архива {archive_path} на части: {str(e)}")
                    bot.edit_message_text("❌ Не удалось разбить архив на части", chat_id, progress_msg_id)
            if backup_state.delete_archive:
                os.remove(archive_path)
        else:
            bot.edit_message_text("❌ Ошибка: архив не найден после создания", chat_id, progress_msg_id)
    elif final_result:
        bot.edit_message_text(f"❌ Ошибка при создании бэкапа: {final_result.get('message', 'Неизвестная ошибка')}", chat_id, progress_msg_id)
    else:
        bot.edit_message_text("❌ Ошибка: скрипт завершился без результата", chat_id, progress_msg_id)

def get_available_drives():
    # Получение списка доступных дисков для бэкапа без swap разделов
    drives = []
    current_drive = None
    current_manufacturer = None

    try:
        media_output = subprocess.check_output(
            ["ndmc", "-c", "show media"],
            text=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return []
    except Exception:
        return []

    for raw_line in media_output.splitlines():
        stripped = raw_line.strip()

        if stripped.startswith("manufacturer:"):
            current_manufacturer = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("uuid:"):
            if current_drive:
                drives.append(current_drive)
            uuid = stripped.split(":", 1)[1].strip()
            current_drive = {'uuid': uuid, 'path': f"/tmp/mnt/{uuid}"}

        elif stripped.startswith("label:") and current_drive is not None:
            current_drive['label'] = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("fstype:") and current_drive is not None:
            fstype = stripped.split(":", 1)[1].strip()
            if fstype == "swap":
                current_drive = None
            else:
                current_drive['fstype'] = fstype

        elif stripped.startswith("free:") and current_drive is not None:
            val = stripped.split(":", 1)[1].strip()
            try:
                size_gb = round(int(val) / (1024 * 1024 * 1024), 1)
            except Exception:
                size_gb = None
            current_drive['size'] = size_gb
            if current_drive.get('label'):
                current_drive['display_name'] = current_drive['label']
            elif current_manufacturer:
                current_drive['display_name'] = current_manufacturer
            else:
                current_drive['display_name'] = "Unknown"

    if current_drive:
        drives.append(current_drive)

    return drives


