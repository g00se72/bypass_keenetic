# g00se72/bypass_keenetic
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/g00se72/bypass_keenetic)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/g00se72/bypass_keenetic)
![GitHub repo size](https://img.shields.io/github/repo-size/g00se72/bypass_keenetic)
![GitHub last commit](https://img.shields.io/github/last-commit/g00se72/bypass_keenetic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/g00se72/bypass_keenetic)
![GitHub top language](https://img.shields.io/github/languages/top/g00se72/bypass_keenetic)

## Описание проекта

Данный репозиторий - это моя версия на основе репозитория от уважаемого [Ziwork](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")

> [!NOTE]  
> **Реализация сделана исключительно для себя, в научно-технических целях**

> [!WARNING]
> Не для коммерческого использования. Автор не несёт ответственности за использование предоставленного материала. Если Вы не согласны с вышеуказанным - немедленно удалите со всех своих устройств любой загруженный из даннного репозитория материал

## Скриншоты
| Главное меню | Ключи и мосты | Списки обхода | Установка и удаление |
|--------------|---------------|---------------|----------------------|
| ![Главное меню](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_MAIN.png) | ![Ключи и мосты](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_VLESS.png) | ![Списки обхода](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_BYPASS_FILES.png) | ![Установка и удаление](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/install_remove_menu.png) |

---

| Сервисное меню | Обновлений нет | Обновления | DNS Override |
|----------------|------------|------------------------|--------------|
| ![Сервисное меню](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_SERVICE.png) | ![Обновления](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/updates_menu.png) | ![Обновления (состояние)](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/updates_menu(need_update).png) | ![DNS Override](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/dns_override_menu.png) |

---

| Бекап меню | Создать бекап | Выбор диска | Удаление архива | Бекап завершен |
|------------|---------------|-------------|-----------------|----------------|
| ![Бекап меню](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_menu.png) | ![Создать бекап](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_menu(backup_state).png) | ![Выбор диска](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/drive_selection_menu.png) | ![Удаление архива](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/delete_archive_menu.png) | ![Бекап завершен](https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_done.png) |

## Установка

> [!TIP]
> При первом подключении по ssh рекомендуется изменить дефолтный пароль командой
> ```bash
> passwd
> ```
>
> Или настроить авторизацию по ssh ключу. Для этого нужно сгенерировать публичный и приватный ключи командой
> ```bash
> ssh-keygen -b 4096
> ```
>
> Создать файл authorized_keys и скопироватьтуда публичную часть ключа
> ```bash
> touch /opt/etc/dropbear/authorized_keys
> ```
> ```bash
> chmod 600 /opt/etc/dropbear/authorized_keys
> ```
>
> После этого авторизацию по паролю можно отключить (добавить ключи -s и -g) в файле /opt/etc/init.d/S51dropbear
> $DROPBEAR -s -g -p $PORT -P $PIDFILE

---

Выполнить команды по очереди
```bash
opkg update
```
```bash
opkg install curl python3 python3-pip
```
```bash
pip3 install --upgrade pip
```
```bash
pip3 install pyTelegramBotAPI telethon pathlib
```

Загрузить бота
```bash
mkdir -p /opt/etc/bot
```
```bash
curl -o /opt/etc/bot/main.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/main.py
```
```bash
curl -o /opt/etc/bot/menu.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/menu.py
```
```bash
curl -o /opt/etc/bot/utils.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/utils.py
```
```bash
curl -o /opt/etc/bot/handlers.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/handlers.py
```
```bash
curl -o /opt/etc/bot/bot_config.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/bot_config.py
```
```bash
chmod 755 /opt/etc/bot
```
```bash
chmod 644 /opt/etc/bot/*.py
```

Заполнить ключ api бота и другие данные для авторизации в telegram через nano или любым другим способом, сохранить файл
```bash
opkg install nano
```
```bash
nano /opt/etc/bot/bot_config.py
```

Запустить бота
```bash
python3 /opt/etc/bot/main.py &
```

Зайти в свой телеграм-бот, нажать `/start`
`📲 Установка и удаление` -> `📲 Установка`

Прогресс установки будет отображаться в телеграм-боте. После завершения установки добавить через бота в списки обхода необходимые вам домены и ip-адреса, в меню бота выбрать `⚙️ Сервис` -> `⁉️ DNS Override` -> `✅ ВКЛ`, после чего роутер перезагрузится

---

> [!TIP]
> Проверить запущен ли бот и узнать <ID_Процесса>
> ```bash
> /opt/etc/init.d/S99telegram_bot status
> ```
> Проверить статус, например, xray можно командой
> ```bash
> /opt/etc/init.d/S24xray status
> ```


>[!NOTE]
>## Ссылки на исходные репозитории
>[https://github.com/ziwork/bypass_keenetic](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")
>[https://github.com/tas-unn/bypass_keenetic](https://github.com/tas-unn/bypass_keenetic "https://github.com/tas-unn/bypass_keenetic")
