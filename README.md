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

## Установка

Выполнить команды по очереди

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

загрузить первую версию бота (оставлю для истории в репозитории)

```bash
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot.py
curl -o /opt/etc/bot_config.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot_config.py

chmod 644 /opt/etc/bot.py
chmod 644 /opt/etc/bot_config.py
```

или любую из новых версий (пока тестируются)

```bash
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot2/bot.py
curl -o /opt/etc/bot_config.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot2/bot_config.py

chmod 644 /opt/etc/bot.py
chmod 644 /opt/etc/bot_config.py
```
```bash
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/main.py
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/menu.py
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/utils.py
curl -o /opt/etc/bot.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/handlers.py
curl -o /opt/etc/bot_config.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/bot_config.py

chmod 755 /opt/etc/bot
chmod 644 /opt/etc/bot/*.py
```

Заполнить ключ api бота и логин из телеграмма через nano или любым другим способом, сохранить файл

```bash
nano /opt/etc/bot_config.py
```

Запустить бота (для версий 1 и 2)

```bash
python3 /opt/etc/bot.py &
```

Запустить бота (для версии 3)

```bash
python3 /opt/etc/bot/main.py &
```

Зайти в свой телеграм-бот, нажать `/start`

`Установка и удаление` -> `Установка` :

Прогресс установки будет отображаться в телеграм-боте

Добавить через бота в списки обхода необходимые вам домены и ip-адреса

В меню бота -> `Сервис` -> `DNS Override` -> `Вкл DNS Override`, после чего роутер перезагрузится

Готово

## Справка

Запустить xray можно командой

```bash
xray run -c /opt/etc/xray/config.json
```

Проверить статус xray

```bash
/opt/etc/init.d/S24xray status
```

Проверить запущен ли бот и узнать <ID_Процесса>

```bash
ps | grep .py
```

Убить процесс бота

```bash
Kill <ID_Процесса>
```

## Ссылки на исходные репозитории

[https://github.com/ziwork/bypass_keenetic](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")

[https://github.com/tas-unn/bypass_keenetic](https://github.com/tas-unn/bypass_keenetic "https://github.com/tas-unn/bypass_keenetic")
