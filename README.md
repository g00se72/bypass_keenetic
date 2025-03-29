# g00se72_bypass_keenetic
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/g00se72/bypass_keenetic)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/g00se72/bypass_keenetic)
![GitHub repo size](https://img.shields.io/github/repo-size/g00se72/bypass_keenetic)
![GitHub last commit](https://img.shields.io/github/last-commit/g00se72/bypass_keenetic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/g00se72/bypass_keenetic)
![GitHub top language](https://img.shields.io/github/languages/top/g00se72/bypass_keenetic)

## Описание проекта

Данный репозиторий - это моя версия на основе репозитория от уважаемого [Ziwork](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")
**!Реализация сделана исключительно для себя, под свои нужды!**

## Скриншоты
<div align="center">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_MAIN.png" alt="Главное меню" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/install_remove_menu.png" alt="Установка и удаление" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_VLESS.png" alt="Ключи и мосты" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_BYPASS_FILES.png" alt="Списки обхода" width="240">
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/MENU_SERVICE.png" alt="Сервисное меню" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/updates_menu.png" alt="Обвновления" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/updates_menu(need_update).png" alt="Обновления" width="240">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/dns_override_menu.png" alt="DNS Override" width="240">
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_menu.png" alt="Бэкап" width="190">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_menu(backup_state).png" alt="Бэкап" width="190">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/drive_selection_menu.png" alt="Бэкап" width="190">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/delete_archive_menu.png" alt="Бэкап" width="190">
  <img src="https://raw.githubusercontent.com/g00se72/bypass_keenetic/e6698361cfea854c4eb049accd524c012df2c9a6/screens/backup_done.png" alt="Бэкап" width="190">
</div>

## Установка

При первом подключении рекомендуется изменить пароль командой

```bash
passwd
```

Выполнить команды по очереди

```bash
opkg update
```

```bash
opkg install curl python3 python3-pip
```

```bash
curl -O https://bootstrap.pypa.io/get-pip.py
```

```bash
python get-pip.py
```

```bash
pip install pyTelegramBotAPI telethon pathlib
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
nano /opt/etc/bot/bot_config.py
```

Запустить бота

```bash
python3 /opt/etc/bot/main.py &
```

Зайти в свой телеграм-бот, нажать `/start`

`📲 Установка и удаление` -> `📲 Установка`

Прогресс установки будет отображаться в телеграм-боте. После завершения установки добавить через бота в списки обхода необходимые вам домены и ip-адреса, в меню бота выбрать `⚙️ Сервис` -> `⁉️ DNS Override` -> `✅ ВКЛ`, после чего роутер перезагрузится

## Справка

Проверить запущен ли бот и узнать <ID_Процесса>

```bash
ps | grep .py
```

Проверить статус, например, xray можно командой

```bash
/opt/etc/init.d/S24xray status
```

## Ссылки на исходные репозитории

[https://github.com/ziwork/bypass_keenetic](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")

[https://github.com/tas-unn/bypass_keenetic](https://github.com/tas-unn/bypass_keenetic "https://github.com/tas-unn/bypass_keenetic")
