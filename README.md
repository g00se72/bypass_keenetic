# g00se72/bypass_keenetic
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/g00se72/bypass_keenetic)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/g00se72/bypass_keenetic)
![GitHub repo size](https://img.shields.io/github/repo-size/g00se72/bypass_keenetic)
![GitHub last commit](https://img.shields.io/github/last-commit/g00se72/bypass_keenetic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/g00se72/bypass_keenetic)
![GitHub top language](https://img.shields.io/github/languages/top/g00se72/bypass_keenetic)

## Описание проекта

Данный репозиторий - это моя версия на основе репозитория от уважаемого [Ziwork](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")

> [!WARNING]
>   
> ***Реализация сделана исключительно для себя, в научно-технических целях. Т.к. пишу и тестирую сам, то возможно мне удается проверить не все возможные сценарии использования. Если Вы решите использовать эти скрипты/бота в своей системе, Вы делаете это полностью на свой страх и риск. Я не несу никакой ответственности за любые прямые или косвенные последствия их использования. Вся ответственность за любые результаты, проблемы или ущерб, возникшие в результате использования, ложится исключительно на Вас. Перед использованием убедительно рекомендуется внимательно изучить код и адаптировать его под свои нужды и условия. При найденных проблемах создавайте Issue. Также для обсуждения открыт функционал Discussions***

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

1) Подготавливаем USB-накопитель по [инструкции](https://help.keenetic.com/hc/ru/articles/360000184259-%D0%9A%D0%B0%D0%BA-%D0%BF%D0%BE%D0%B4%D0%B3%D0%BE%D1%82%D0%BE%D0%B2%D0%B8%D1%82%D1%8C-USB-%D0%BD%D0%B0%D0%BA%D0%BE%D0%BF%D0%B8%D1%82%D0%B5%D0%BB%D1%8C-%D0%B4%D0%BB%D1%8F-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%B2-%D0%BA%D0%B0%D1%87%D0%B5%D1%81%D1%82%D0%B2%D0%B5-%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D0%BB%D0%B8%D1%89%D0%B0-%D0%B8-%D0%BE%D0%B4%D0%BD%D0%BE%D0%B2%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D0%BE-%D1%80%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%B8%D1%8F-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BC%D0%B0-%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D0%BE%D0%B9-%D0%BF%D0%B0%D0%BC%D1%8F%D1%82%D0%B8-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82-%D1%86%D0%B5%D0%BD%D1%82%D1%80%D0%B0). В качестве USB-накопителя рекомендую использовать жесткий диск, а не флеш-накопитель

> [!IMPORTANT]
> 
> Во избежании проблем с нехваткой памяти рекомендую именно эту инструкцию с созданием SWAP-раздела. Если у вас "хорошее" железо и вы уверены, что создание SWAP-раздела не нужно, просто пропустите создание SWAP-раздела в инструкции

2) Устанавливаем Entware по [инструкции](https://help.keenetic.com/hc/ru/articles/360021214160-%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%D0%BE%D0%B2-%D1%80%D0%B5%D0%BF%D0%BE%D0%B7%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D1%8F-Entware-%D0%BD%D0%B0-USB-%D0%BD%D0%B0%D0%BA%D0%BE%D0%BF%D0%B8%D1%82%D0%B5%D0%BB%D1%8C)

> [!TIP]
> 
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
> Создать файл authorized_keys и скопировать туда публичную часть ключа
> ```bash
> touch /opt/etc/dropbear/authorized_keys
> ```
> ```bash
> chmod 600 /opt/etc/dropbear/authorized_keys
> ```
>
> После этого авторизацию по паролю можно отключить (добавить ключи -s и -g) в файле /opt/etc/init.d/S51dropbear
> > $DROPBEAR -s -g -p $PORT -P $PIDFILE

---

3) Выполнить команды для установки компонентов по очереди
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
pip3 install pyTelegramBotAPI==4.27.0
```

4) Загрузить бота
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

5) Заполнить ключ api бота и другие данные для авторизации в telegram через nano или любым другим способом, сохранить файл
```bash
opkg install nano
```
```bash
nano /opt/etc/bot/bot_config.py
```

6) Запустить бота
```bash
python3 /opt/etc/bot/main.py &
```

7) Зайти в свой телеграм-бот, нажать `/start`
`📲 Установка и удаление` -> `📲 Установка`

Прогресс установки будет отображаться в телеграм-боте. После завершения установки добавить через бота в списки обхода необходимые вам домены и ip-адреса, в меню бота выбрать `⚙️ Сервис` -> `⁉️ DNS Override` -> `✅ ВКЛ`, после чего роутер перезагрузится

---

> [!TIP]
> 
> Проверить запущен ли бот и узнать <ID_Процесса>
> ```bash
> /opt/etc/init.d/S99telegram_bot status
> ```
> Проверить статус, например, xray можно командой
> ```bash
> /opt/etc/init.d/S24xray status
> ```


>[!NOTE]
>
> Для восстановления настроек из бекапа:
> 1) **Конфигурация.** Откройте веб-конфигуратор роутера, перейдите в меню `Управление` -> `Параметры системы`. В разделе `Системные файлы` загрузите бекап файла конфигурации в устройство
> 2) **Прошивка.** Откройте веб-конфигуратор роутера, перейдите в меню `Управление` -> `Параметры системы`. В разделе `Системные файлы` загрузите бекап файла прошивки в устройство
> 3) **Entware.** Воспользуйтесь [инструкцией](https://help.keenetic.com/hc/ru/articles/360021214160-%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%D0%BE%D0%B2-%D1%80%D0%B5%D0%BF%D0%BE%D0%B7%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D1%8F-Entware-%D0%BD%D0%B0-USB-%D0%BD%D0%B0%D0%BA%D0%BE%D0%BF%D0%B8%D1%82%D0%B5%D0%BB%D1%8C). Пропустите шаг №3 и на шаге №4 инструкции используйте ваш файл бекапа Entware `mipsel-installer.tar.gz` `mips-installer.tar.gz` `aarch64-installer.tar.gz`
> 4) **Другие файлы.** Список файлов и дерикторий для бекапа определяет пользователь в bot_config.py. Поэтому порядок восстановления будет зависеть от того, что будете бекапить. По-умолчанию бекапятся файлы бота, скриптов, настройки vless и tor

>[!NOTE]
>
> Ссылки на исходные репозитории\
>[https://github.com/ziwork/bypass_keenetic](https://github.com/ziwork/bypass_keenetic "https://github.com/ziwork/bypass_keenetic")\
>[https://github.com/tas-unn/bypass_keenetic](https://github.com/tas-unn/bypass_keenetic "https://github.com/tas-unn/bypass_keenetic")
