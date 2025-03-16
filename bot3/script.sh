#!/bin/sh

# читаем переменные
lanip=$(ip addr show br0 | grep -Po "(?<=inet ).*(?=/)" | awk '{print $1}')
localportsh=$(grep "localportsh" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
#dnsporttor=$(grep "dnsporttor" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localporttor=$(grep "localporttor" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localportvless=$(grep "localportvless" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localporttrojan=$(grep "localporttrojan" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
dnsovertlsport=$(grep "dnsovertlsport" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
dnsoverhttpsport=$(grep "dnsoverhttpsport" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
keen_os_full=$(curl -s localhost:79/rci/show/version/title | tr -d \",)
keen_os_short=$(echo "$keen_os_full" | cut -b 1)


if [ "$1" = "-restart" ]; then
    bot_pid=$(ps | grep "[p]ython3 /opt/etc/bot/main.py" | awk '{print $1}')
    [ -n "$bot_pid" ] && echo "Останавливаем бота..." && kill "$bot_pid" && sleep 5
    
    python3 /opt/etc/bot/main.py &
    check_running=$(ps | grep "[p]ython3 /opt/etc/bot/main.py")
    if [ -n "$check_running" ]; then
        echo "Бот запущен. Нажмите на /start"
        exit 0
    else
        echo "Ошибка: бот не запустился"
        exit 1
    fi
fi


if [ "$1" = "-remove" ]; then
    echo "Начинаем удаление"
    for pkg in tor tor-geoip bind-dig cron dnsmasq-full ipset iptables obfs4 shadowsocks-libev-ss-redir shadowsocks-libev-config xray trojan; do
    if opkg list-installed | grep -q "^$pkg "; then
        echo "Удаляем пакет: $pkg"
        opkg remove "$pkg" #--force-removal-of-dependent-packages
    else
        echo "Пакет $pkg не установлен, пропускаем..."
    fi
    done
    echo "Все пакеты удалены. Начинаем удаление папок, файлов и настроек"
	
    ipset flush unblocktor
    ipset flush unblocksh
    ipset flush unblockvless
    ipset flush unblocktroj
	
    if ls -d /opt/etc/unblock/vpn-*.txt >/dev/null 2>&1; then
        for vpn_file_names in /opt/etc/unblock/vpn-*; do
            vpn_file_name=$(echo "$vpn_file_names" | awk -F '/' '{print $5}' | sed 's/.txt//')
            unblockvpn=$(echo unblock"$vpn_file_name")
            ipset flush "$unblockvpn"
        done
    fi

    # Список для удаления
    for file in \
        "/opt/etc/crontab" \
        "/opt/etc/init.d/S22shadowsocks" \
        "/opt/etc/init.d/S22trojan" \
        "/opt/etc/init.d/S24xray" \
        "/opt/etc/init.d/S35tor" \
        "/opt/etc/init.d/S56dnsmasq" \
        "/opt/etc/init.d/S99unblock" \
        "/opt/etc/ndm/netfilter.d/100-redirect.sh" \
        "/opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh" \
        "/opt/etc/nmd/fs.d/100-ipset.sh" \
        "/opt/bin/unblock_dnsmasq.sh" \
        "/opt/bin/unblock_update.sh" \
        "/opt/bin/unblock_ipset.sh" \
        "/opt/etc/unblock.dnsmasq" \
        "/opt/etc/dnsmasq.conf" \
        "/opt/tmp/tor" \
        "/opt/etc/tor" \
        "/opt/etc/xray" \
        "/opt/etc/trojan"
    do
        [ -e "$file" ] && rm -rf "$file"
    done
    echo "Созданные папки, файлы и настройки удалены"
    echo "Если вы хотите полностью отключить DNS Override, перейдите в меню Сервис -> DNS Override -> DNS Override ВЫКЛ. После чего включится встроенный (штатный) DNS и роутер перезагрузится"
    exit 0
fi


if [ "$1" = "-install" ]; then
    echo "Начинаем установку"
    echo "Ваша версия KeenOS" "${keen_os_full}"
    for pkg in curl tor tor-geoip bind-dig cron dnsmasq-full ipset iptables obfs4 shadowsocks-libev-ss-redir shadowsocks-libev-config xray trojan; do
        if opkg list-installed | grep -q "^$pkg "; then
            echo "Пакет $pkg уже установлен, пропускаем..."
        else
            if ! opkg install "$pkg"; then
                echo "Ошибка при установке пакета $pkg" >&2
                exit 1
            fi
        fi
    done
    sleep 3
    echo "Установка пакетов завершена. Продолжаем установку"

    # есть поддержка множества hash:net или нет, если нет, то при этом вы потеряете возможность разблокировки по диапазону и CIDR
    set_type=$(ipset --help 2>/dev/null | grep -q "hash:net" && echo "hash:net" || echo "hash:ip")
    [ "$set_type" = "hash:net" ] && echo "Поддержка множества типа hash:net есть" || echo "Поддержка множества типа hash:net отсутствует"
    
    # создание множеств IP-адресов unblock 
    curl -o /opt/etc/ndm/fs.d/100-ipset.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/100-ipset.sh || exit 1
    sed -i "s/hash:net/${set_type}/g" /opt/etc/ndm/fs.d/100-ipset.sh && \
    echo "Созданы файлы под множества"
    chmod 755 /opt/etc/ndm/fs.d/100-ipset.sh || chmod +x /opt/etc/ndm/fs.d/100-ipset.sh

    mkdir -p /opt/tmp/tor
    curl -o /opt/etc/tor/torrc https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/torrc && \
    sed -i "s/hash:net/${set_type}/g" /opt/etc/tor/torrc && \
    echo "Установлены базовые настройки Tor"

    curl -o /opt/etc/shadowsocks.json https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/shadowsocks.json && \
    sed -i "s/ss-local/ss-redir/g" /opt/etc/init.d/S22shadowsocks && \
    echo "Установлены базовые настройки Shadowsocks"
    chmod 755 /opt/etc/init.d/S22shadowsocks || chmod +x /opt/etc/init.d/S22shadowsocks

    curl -o /opt/etc/trojan/config.json https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/trojanconfig.json && \
    echo "Установлены базовые настройки Trojan"
    
    curl -o /opt/etc/xray/config.json https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/vlessconfig.json && \
    sed -i 's|ARGS="run -confdir /opt/etc/xray"|ARGS="run -c /opt/etc/xray/config.json"|' /opt/etc/init.d/S24xray > /dev/null && \
    echo "Установлены базовые настройки Xray"
    chmod 755 /opt/etc/init.d/S24xray || chmod +x /opt/etc/init.d/S24xray

    # создание unblock папки и файлов под домены и ip-адреса
    mkdir -p /opt/etc/unblock
    # если не нужны списки с git строки можно закоментиовать, если нужны - оставить, команда touch не изменит их содержимое, только метку времени
    curl -o /opt/etc/unblock/vless.txt https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/unblockvless.txt
    curl -o /opt/etc/unblock/tor.txt https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/unblocktor.txt
    for file in \
        "/opt/etc/hosts" \
        "/opt/etc/unblock/shadowsocks.txt" \
        "/opt/etc/unblock/tor.txt" \
        "/opt/etc/unblock/trojan.txt" \
        "/opt/etc/unblock/vless.txt" \
        "/opt/etc/unblock/vpn.txt"
    do
	touch "$file" && chmod 644 "$file"
    done
    echo "Созданы файлы под домены и ip-адреса"

    # unblock_ipset.sh
    curl -o /opt/bin/unblock_ipset.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/unblock_ipset.sh || exit 1
    sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_ipset.sh && \
    echo "Установлен скрипт для заполнения множеств unblock IP-адресами заданного списка доменов"
    chmod 755 /opt/bin/unblock_ipset.sh || chmod +x /opt/bin/unblock_ipset.sh

    # unblock_dnsmasq.sh
    curl -o /opt/bin/unblock_dnsmasq.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/unblock.dnsmasq.sh || exit 1
    sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_dnsmasq.sh && \
    echo "Установлен скрипт для формирования дополнительного конфигурационного файла dnsmasq из заданного списка доменов и его запуск"
    chmod 755 /opt/bin/unblock_dnsmasq.sh || chmod +x /opt/bin/unblock_dnsmasq.sh
    /opt/bin/unblock_dnsmasq.sh

    # unblock_update.sh
    curl -o /opt/bin/unblock_update.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/unblock_update.sh || exit 1
    echo "Установлен скрипт ручного принудительного обновления системы после редактирования списка доменов"
    chmod 755 /opt/bin/unblock_update.sh || chmod +x /opt/bin/unblock_update.sh

    # s99unblock
    curl -o /opt/etc/init.d/S99unblock https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/S99unblock || exit 1
    echo "Установлен cкрипт автоматического заполнения множества unblock при загрузке маршрутизатора"
    chmod 755 /opt/etc/init.d/S99unblock || chmod +x /opt/etc/init.d/S99unblock

    # 100-redirect.sh
    curl -o /opt/etc/ndm/netfilter.d/100-redirect.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/100-redirect.sh || exit 1
    sed -i -e "s/hash:net/${set_type}/g" \
           -e "s/192.168.1.1/${lanip}/g" \
           -e "s/1082/${localportsh}/g" \
           -e "s/9141/${localporttor}/g" \
           -e "s/10810/${localportvless}/g" \
           -e "s/10829/${localporttrojan}/g" \
           /opt/etc/ndm/netfilter.d/100-redirect.sh && \
    echo "Установлено перенаправление пакетов с адресатами из unblock в Tor, Shadowsocks, VPN, Trojan, Xray"
    chmod 755 /opt/etc/ndm/netfilter.d/100-redirect.sh || chmod +x /opt/etc/ndm/netfilter.d/100-redirect.sh

    # VPN script
    if [ "${keen_os_short}" = "4" ]; then
          echo "VPN для KeenOS 4+";
          curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/100-unblock-vpn-v4.sh || exit 1
    else
          echo "VPN для KeenOS 3";
          curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/100-unblock-vpn.sh || exit 1
    fi
    echo "Установлен скрипт проверки подключения и остановки VPN"
    chmod 755 /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh || chmod +x /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh

    # dnsmasq.conf
    rm -f /opt/etc/dnsmasq.conf
    curl -o /opt/etc/dnsmasq.conf https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/dnsmasq.conf || exit 1
    sed -i -e "s/192.168.1.1/${lanip}/g" -e "s/40500/${dnsovertlsport}/g" -e "s/40508/${dnsoverhttpsport}/g" /opt/etc/dnsmasq.conf && \
    echo "Установлена настройка dnsmasq и подключение дополнительного конфигурационного файла к dnsmasq"
    chmod 644 /opt/etc/dnsmasq.conf

    # cron file
    rm -f /opt/etc/crontab
    curl -o /opt/etc/crontab https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/crontab || exit 1
    echo "Добавлены задачи в cron для периодического обновления содержимого множества"
    chmod 644 /opt/etc/crontab
    /opt/bin/unblock_update.sh
    echo "Установлены все изначальные скрипты и скрипты разблокировок, выполнена основная настройка бота"
    
    exit 0
fi


if [ "$1" = "-update" ]; then
    echo "Начинаем обновление"
    #opkg update > /dev/null 2>&1 && echo "Пакеты обновлены"
    echo "Ваша версия KeenOS" "${keen_os_full}"

    #/opt/etc/init.d/S22shadowsocks stop > /dev/null 2>&1 || echo "S22shadowsocks не найден, пропускаем остановку"
    #/opt/etc/init.d/S24xray stop > /dev/null 2>&1 || echo "S24xray не найден, пропускаем остановку"
    #/opt/etc/init.d/S22trojan stop > /dev/null 2>&1 || echo "S22trojan не найден, пропускаем остановку"
    #/opt/etc/init.d/S35tor stop > /dev/null 2>&1 || echo "S35tor не найден, пропускаем остановку"
    #echo "Сервисы остановлены"

    now=$(date +"%Y.%m.%d.%H-%M")
    backup_dir="/opt/root/backup-${now}"
    mkdir -p "${backup_dir}"
    # Массив с путями к файлам, которые будут обновлены
    for file in \
        "/opt/etc/bot/main.py" \
        "/opt/etc/bot/menu.py" \
        "/opt/etc/bot/utils.py" \
        "/opt/etc/bot/handlers.py"
    do
        if [ -e "$file" ]; then
            mv "$file" "${backup_dir}/$(basename "$file")"
        fi
    done
    echo "Бэкап создан"
	
    #что нужно обновить
    curl -s -o /opt/etc/bot/main.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/main.py || exit 1
    curl -s -o /opt/etc/bot/menu.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/maenu.py || exit 1
    curl -s -o /opt/etc/bot/utils.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/utils.py || exit 1
    curl -s -o /opt/etc/bot/handlers.py https://raw.githubusercontent.com/g00se72/bypass_keenetic/main/bot3/handlers.py || exit 1
    echo "Обновления загружены"
    chmod 755 /opt/etc/bot
    chmod 644 /opt/etc/bot/*.py

    #/opt/etc/init.d/S56dnsmasq restart > /dev/null 2>&1 || echo "Ошибка при перезапуске dnsmasq"
    #/opt/etc/init.d/S22shadowsocks start > /dev/null 2>&1 || echo "S22shadowsocks не запущен, проверьте конфигурацию, пропускаем остановку"
    #/opt/etc/init.d/S24xray start > /dev/null 2>&1 || echo "S24xray не запущен, проверьте конфигурацию, пропускаем остановку"
    #/opt/etc/init.d/S22trojan start > /dev/null 2>&1 || echo "S22trojan не запущен, проверьте конфигурацию, пропускаем остановку"
    #/opt/etc/init.d/S35tor start > /dev/null 2>&1 || echo "S35tor не запущен, проверьте конфигурацию, пропускаем остановку"

    bot_old_version=$(grep "ВЕРСИЯ" /opt/etc/bot/bot_config.py | grep -Eo "[0-9].{1,}")
    bot_new_version=$(grep "ВЕРСИЯ" /opt/etc/bot/main.py | grep -Eo "[0-9].{1,}")

    echo "Версия " "${bot_old_version}" " обновлена до " "${bot_new_version}"
    sleep 2
    sed -i "s/${bot_old_version}/${bot_new_version}/g" /opt/etc/bot/bot_config.py
    echo "Обновление выполнено. Сервисы перезапущены. Сейчас будет перезапущен бот (~15-30 сек)"
    sleep 2
    /bin/sh /opt/root/script.sh -restart || exit 1

    exit 0
fi


if [ "$1" = "-version" ]; then
    echo "Ваша версия KeenOS" "${keen_os_full}"
fi


if [ "$1" = "-help" ]; then
    echo "-install для установки"
    echo "-remove для удаления"
    echo "-update для обновления"
    echo "-version узнать версию KeenOS"
    echo "-restart перезапустить бота"
fi


if [ -z "$1" ]; then
    echo "-help посмотреть список доступных аргументов"
fi
