#!/bin/sh

repo="g00se72"

# ip роутера
lanip=$(ip addr show br0 | grep -Po "(?<=inet ).*(?=/)" | awk '{print $1}')
ssredir="ss-redir"
localportsh=$(grep "localportsh" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
#dnsporttor=$(grep "dnsporttor" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localporttor=$(grep "localporttor" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localportvless=$(grep "localportvless" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
localporttrojan=$(grep "localporttrojan" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
dnsovertlsport=$(grep "dnsovertlsport" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
dnsoverhttpsport=$(grep "dnsoverhttpsport" /opt/etc/bot_config.py | grep -Eo "[0-9]{1,5}")
keen_os_full=$(curl -s localhost:79/rci/show/version/title | tr -d \",)
keen_os_short=$(curl -s localhost:79/rci/show/version/title | tr -d \", | cut -b 1)


if [ "$1" = "-remove" ]; then
    echo "Начинаем удаление"
    opkg remove tor tor-geoip bind-dig cron dnsmasq-full ipset iptables obfs4 shadowsocks-libev-ss-redir shadowsocks-libev-config xray trojan
    echo "Пакеты удалены, удаляем папки, файлы и настройки"
	
    ipset flush testset
    ipset flush unblocktor
    ipset flush unblocksh
    ipset flush unblockvless
    ipset flush unblocktroj
    #ipset flush unblockvpn
	
    if ls -d /opt/etc/unblock/vpn-*.txt >/dev/null 2>&1; then
     for vpn_file_names in /opt/etc/unblock/vpn-*; do
     vpn_file_name=$(echo "$vpn_file_names" | awk -F '/' '{print $5}' | sed 's/.txt//')
     #shellcheck disable=SC2116
     unblockvpn=$(echo unblock"$vpn_file_name")
     ipset flush "$unblockvpn"
     done
    fi

    #chmod 777 /opt/root/get-pip.py || rm -Rfv /opt/root/get-pip.py
    chmod 777 /opt/etc/crontab || rm -Rfv /opt/etc/crontab
    chmod 777 /opt/etc/init.d/S22shadowsocks || rm -Rfv /opt/etc/init.d/S22shadowsocks
    chmod 777 /opt/etc/init.d/S22trojan || rm -Rfv /opt/etc/init.d/S22trojan
    chmod 777 /opt/etc/init.d/S24xray || rm -Rfv /opt/etc/init.d/S24xray
    chmod 777 /opt/etc/init.d/S35tor || rm -Rfv /opt/etc/init.d/S35tor
    chmod 777 /opt/etc/init.d/S56dnsmasq || rm -Rfv /opt/etc/init.d/S56dnsmasq
    chmod 777 /opt/etc/init.d/S99unblock || rm -Rfv /opt/etc/init.d/S99unblock
    chmod 777 /opt/etc/ndm/netfilter.d/100-redirect.sh || rm -rfv /opt/etc/ndm/netfilter.d/100-redirect.sh
    chmod 777 /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh || rm -rfv /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh
    chmod 777 /opt/etc/nmd/fs.d/100-ipset.sh || rm -rfv /opt/etc/nmd/fs.d/100-ipset.sh
    chmod 777 /opt/bin/unblock_dnsmasq.sh || rm -rfv /opt/bin/unblock_dnsmasq.sh
    chmod 777 /opt/bin/unblock_update.sh || rm -rfv /opt/bin/unblock_update.sh
    chmod 777 /opt/bin/unblock_ipset.sh || rm -rfv /opt/bin/unblock_ipset.sh
    chmod 777 /opt/etc/unblock.dnsmasq || rm -rfv /opt/etc/unblock.dnsmasq
    chmod 777 /opt/etc/dnsmasq.conf || rm -rfv /opt/etc/dnsmasq.conf
    chmod 777 /opt/tmp/tor || rm -Rfv /opt/tmp/tor
    #chmod 777 /opt/etc/unblock || rm -Rfv /opt/etc/unblock
    chmod 777 /opt/etc/tor || rm -Rfv /opt/etc/tor
    chmod 777 /opt/etc/xray || rm -Rfv /opt/etc/xray
    chmod 777 /opt/etc/trojan || rm -Rfv /opt/etc/trojan
    echo "Созданные папки, файлы и настройки удалены"
    echo "Если вы хотите полностью отключить DNS Override, перейдите в меню Сервис -> DNS Override -> DNS Override ВЫКЛ. После чего включится встроенный (штатный) DNS и роутер перезагрузится"
    exit 0
fi


if [ "$1" = "-install" ]; then
    echo "Начинаем установку"
    echo "Ваша версия KeenOS" "${keen_os_full}"
    opkg update
    opkg install curl tor tor-geoip bind-dig cron dnsmasq-full ipset iptables obfs4 shadowsocks-libev-ss-redir shadowsocks-libev-config xray trojan
   
    sleep 3
    echo "Установка пакетов завершена. Продолжаем установку"

    # есть поддержка множества hash:net или нет, если нет, то при этом вы потеряете возможность разблокировки по диапазону и CIDR
    set_type="hash:net"
    ipset create testset hash:net -exist > /dev/null 2>&1
    retVal=$?
    if [ $retVal -ne 0 ]; then
        set_type="hash:ip"
    fi

    echo "Переменные роутера найдены"
    # создания множеств IP-адресов unblock 
    curl -o /opt/etc/ndm/fs.d/100-ipset.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-ipset.sh
    chmod 755 /opt/etc/ndm/fs.d/100-ipset.sh || chmod +x /opt/etc/ndm/fs.d/100-ipset.sh
    sed -i "s/hash:net/${set_type}/g" /opt/etc/ndm/fs.d/100-ipset.sh
    echo "Созданы файлы под множества"

    mkdir -p /opt/tmp/tor
    curl -o /opt/etc/tor/torrc https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/torrc
    sed -i "s/hash:net/${set_type}/g" /opt/etc/tor/torrc
    echo "Установлены настройки Tor"

    curl -o /opt/etc/shadowsocks.json https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/shadowsocks.json
    sed -i "s/ss-local/${ssredir}/g" /opt/etc/init.d/S22shadowsocks
    chmod 0755 /opt/etc/shadowsocks.json || chmod 755 /opt/etc/init.d/S22shadowsocks || chmod +x /opt/etc/init.d/S22shadowsocks
    echo "Установлены настройки Shadowsocks"
    curl -o /opt/etc/trojan/config.json https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/trojanconfig.json
    echo "Установлены настройки Trojan"
    curl -o /opt/etc/xray/config.json https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/vlessconfig.json
    chmod 755 /opt/etc/init.d/S24xray || chmod +x /opt/etc/init.d/S24xray
    sed -i 's|ARGS="-confdir /opt/etc/xray"|ARGS="run -c /opt/etc/xray/config.json"|g' /opt/etc/init.d/S24xray > /dev/null 2>&1
    echo "Установлены настройки Xray"
    
    # unblock folder and files
    mkdir -p /opt/etc/unblock
    touch /opt/etc/hosts || chmod 0755 /opt/etc/hosts
    touch /opt/etc/unblock/shadowsocks.txt || chmod 0755 /opt/etc/unblock/shadowsocks.txt
    touch /opt/etc/unblock/tor.txt || chmod 0755 /opt/etc/unblock/tor.txt
    touch /opt/etc/unblock/trojan.txt || chmod 0755 /opt/etc/unblock/trojan.txt
    touch /opt/etc/unblock/vless.txt || chmod 0755 /opt/etc/unblock/vless.txt
    touch /opt/etc/unblock/vpn.txt || chmod 0755 /opt/etc/unblock/vpn.txt
    echo "Созданы файлы под сайты и ip-адреса для обхода блокировок для SS, Tor, Trojan и xray, VPN"

    # unblock_ipset.sh
    curl -o /opt/bin/unblock_ipset.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock_ipset.sh
    chmod 755 /opt/bin/unblock_ipset.sh || chmod +x /opt/bin/unblock_ipset.sh
    sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_ipset.sh
    echo "Установлен скрипт для заполнения множеств unblock IP-адресами заданного списка доменов"

    # unblock_dnsmasq.sh
    curl -o /opt/bin/unblock_dnsmasq.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock.dnsmasq.sh
    chmod 755 /opt/bin/unblock_dnsmasq.sh || chmod +x /opt/bin/unblock_dnsmasq.sh
    sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_dnsmasq.sh
    /opt/bin/unblock_dnsmasq.sh
    echo "Установлен скрипт для формирования дополнительного конфигурационного файла dnsmasq из заданного списка доменов и его запуск"

    # unblock_update.sh
    curl -o /opt/bin/unblock_update.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock_update.sh
    chmod 755 /opt/bin/unblock_update.sh || chmod +x /opt/bin/unblock_update.sh
    echo "Установлен скрипт ручного принудительного обновления системы после редактирования списка доменов"

    # s99unblock
    curl -o /opt/etc/init.d/S99unblock https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/S99unblock
    chmod 755 /opt/etc/init.d/S99unblock || chmod +x /opt/etc/init.d/S99unblock
    echo "Установлен cкрипт автоматического заполнения множества unblock при загрузке маршрутизатора"

    # 100-redirect.sh
    curl -o /opt/etc/ndm/netfilter.d/100-redirect.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-redirect.sh
    chmod 755 /opt/etc/ndm/netfilter.d/100-redirect.sh || chmod +x /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/hash:net/${set_type}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/192.168.1.1/${lanip}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/1082/${localportsh}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/9141/${localporttor}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/10810/${localportvless}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    sed -i "s/10829/${localporttrojan}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    echo "Установлено перенаправление пакетов с адресатами из unblock в Tor, Shadowsocks, VPN, Trojan, xray"

    # VPN script
    if [ "${keen_os_short}" = "4" ]; then
      echo "VPN для KeenOS 4+";
      curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn-v4.sh
    elif [ "${keen_os_short}" = "3" ]; then
      echo "VPN для KeenOS 3+";
      curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn.sh
    else
      echo "Версия KeenOS неопределена, будет установлен скрипт для KeenOS 3+";
      curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn.sh
    fi
    chmod 755 /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh || chmod +x /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh
    echo "Установлен скрипт проверки подключения и остановки VPN"

    # dnsmasq.conf
    chmod 777 /opt/etc/dnsmasq.conf || rm -rfv /opt/etc/dnsmasq.conf
    curl -o /opt/etc/dnsmasq.conf https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/dnsmasq.conf
    chmod 755 /opt/etc/dnsmasq.conf
    sed -i "s/192.168.1.1/${lanip}/g" /opt/etc/dnsmasq.conf
    sed -i "s/40500/${dnsovertlsport}/g" /opt/etc/dnsmasq.conf
    sed -i "s/40508/${dnsoverhttpsport}/g" /opt/etc/dnsmasq.conf
    echo "Установлена настройка dnsmasq и подключение дополнительного конфигурационного файла к dnsmasq"

    # cron file
    chmod 777 /opt/etc/crontab || rm -Rfv /opt/etc/crontab
    curl -o /opt/etc/crontab https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/crontab
    chmod 755 /opt/etc/crontab
    echo "Установлено добавление задачи в cron для периодического обновления содержимого множества"
    /opt/bin/unblock_update.sh
    echo "Установлены все изначальные скрипты и скрипты разблокировок, выполнена основная настройка бота"
    
    exit 0
fi

#if [ "$1" = "-reinstall" ]; then
#    curl -s -o /opt/root/script.sh https://raw.githubusercontent.com/ziwork/bypass_keenetic/main/script.sh
#    chmod 755 /opt/root/script.sh || chmod +x /opt/root/script.sh
#    echo "Начинаем переустановку"
#    echo "Удаляем установленные пакеты и созданные файлы"
#    /bin/sh /opt/root/script.sh -remove
#    echo "Удаление завершено"
#    echo "Выполняем установку"
#    /bin/sh /opt/root/script.sh -install
#    echo "Установка выполнена."
#    exit 0
#fi


if [ "$1" = "-update" ]; then
    echo "Начинаем обновление"
    #opkg update > /dev/null 2>&1
    echo "Ваша версия KeenOS" "${keen_os_full}"
    #echo "Пакеты обновлены"

    #/opt/etc/init.d/S22shadowsocks stop > /dev/null 2>&1
    #/opt/etc/init.d/S24xray stop > /dev/null 2>&1
    #/opt/etc/init.d/S22trojan stop > /dev/null 2>&1
    #/opt/etc/init.d/S35tor stop > /dev/null 2>&1
    #echo "Сервисы остановлены"

    now=$(date +"%Y.%m.%d.%H-%M")
    mkdir /opt/root/backup-"${now}"
	
    #опредлить то, что нужно бекапить
    #mv /opt/bin/unblock_ipset.sh /opt/root/backup-"${now}"/unblock_ipset.sh
    #mv /opt/bin/unblock_dnsmasq.sh /opt/root/backup-"${now}"/unblock_dnsmasq.sh
    #mv /opt/bin/unblock_update.sh /opt/root/backup-"${now}"/unblock_update.sh
    #mv /opt/etc/dnsmasq.conf /opt/root/backup-"${now}"/dnsmasq.conf
    #mv /opt/etc/ndm/fs.d/100-ipset.sh /opt/root/backup-"${now}"/100-ipset.sh
    #mv /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh /opt/root/backup-"${now}"/100-unblock-vpn.sh
    #mv /opt/etc/ndm/netfilter.d/100-redirect.sh /opt/root/backup-"${now}"/100-redirect.sh
    mv /opt/etc/bot.py /opt/root/backup-"${now}"/bot.py
    #rm -R /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn > /dev/null 2>&1
    chmod 755 /opt/root/backup-"${now}"/*
    echo "Бэкап создан"
	
    #список действий по обновлению
    #touch /opt/etc/hosts || chmod 0755 /opt/etc/hosts
    #curl -s -o /opt/etc/ndm/fs.d/100-ipset.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-ipset.sh
    #chmod 755 /opt/etc/ndm/fs.d/100-ipset.sh || chmod +x /opt/etc/ndm/fs.d/100-ipset.sh
    #curl -s -o /opt/etc/ndm/netfilter.d/100-redirect.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-redirect.sh
    #chmod 755 /opt/etc/ndm/netfilter.d/100-redirect.sh || chmod +x /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/hash:net/${set_type}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/192.168.1.1/${lanip}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/1082/${localportsh}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/9141/${localporttor}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/10810/${localportvless}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i "s/10829/${localporttrojan}/g" /opt/etc/ndm/netfilter.d/100-redirect.sh
    #sed -i 's|ARGS="-confdir /opt/etc/xray"|ARGS="run -c /opt/etc/xray/config.json"|g' /opt/etc/init.d/S24xray > /dev/null 2>&1

    #if [ "${keen_os_short}" = "4" ]; then
    #  echo "KeenOS 4+";
    #  curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn-v4.sh
    #elif [ "${keen_os_short}" = "3" ]; then
    #  echo "KeenOS 3+";
    #  curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn.sh
    #else
    #  echo "Версия KeenOS неопределена, будет установлен скрипт для KeenOS 3+";
    #  curl -s -o /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/100-unblock-vpn.sh
    #fi
    #chmod 755 /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh || chmod +x /opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh

    #curl -s -o /opt/bin/unblock_ipset.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock_ipset.sh
    #curl -s -o /opt/bin/unblock_dnsmasq.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock.dnsmasq.sh
    #curl -s -o /opt/bin/unblock_update.sh https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/unblock_update.sh
    #chmod 755 /opt/bin/unblock_*.sh || chmod +x /opt/bin/unblock_*.sh
    #sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_ipset.sh
    #sed -i "s/40500/${dnsovertlsport}/g" /opt/bin/unblock_dnsmasq.sh

    #curl -s -o /opt/etc/dnsmasq.conf https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/dnsmasq.conf
    #chmod 755 /opt/etc/dnsmasq.conf
    #sed -i "s/192.168.1.1/${lanip}/g" /opt/etc/dnsmasq.conf
    #sed -i "s/40500/${dnsovertlsport}/g" /opt/etc/dnsmasq.conf
    #sed -i "s/40508/${dnsoverhttpsport}/g" /opt/etc/dnsmasq.conf

    curl -s -o /opt/etc/bot.py https://raw.githubusercontent.com/${repo}/bypass_keenetic/main/bot.py
    chmod 755 /opt/etc/bot.py
    echo "Обновления загружены, права настроены"

    #/opt/etc/init.d/S56dnsmasq restart > /dev/null 2>&1
    #/opt/etc/init.d/S22shadowsocks start > /dev/null 2>&1
    #/opt/etc/init.d/S24xray start > /dev/null 2>&1
    #/opt/etc/init.d/S22trojan start > /dev/null 2>&1
    #/opt/etc/init.d/S35tor start > /dev/null 2>&1

    bot_old_version=$(grep "ВЕРСИЯ" /opt/etc/bot_config.py | grep -Eo "[0-9].{1,}")
    bot_new_version=$(grep "ВЕРСИЯ" /opt/etc/bot.py | grep -Eo "[0-9].{1,}")

    echo "Версия " "${bot_old_version}" " обновлена до " "${bot_new_version}"
    sleep 2
    sed -i "s/${bot_old_version}/${bot_new_version}/g" /opt/etc/bot_config.py
    echo "Обновление выполнено. Сервисы перезапущены. Сейчас будет перезапущен бот (~15-30 сек)"
    sleep 7

    bot_pid=$(ps | grep "[p]ython3 /opt/etc/bot.py" | awk '{print $1}')
    [ -n "$bot_pid" ] && echo "Останавливаем бота..." && kill "$bot_pid" && sleep 5
    
    python3 /opt/etc/bot.py &
    check_running=$(ps | grep "[p]ython3 /opt/etc/bot.py")
    [ -n "$(ps | grep '[p]ython3 /opt/etc/bot.py')" ] && echo "Бот запущен. Нажмите на /start" || echo "Ошибка: бот не запустился"

    exit 0
fi


if [ "$1" = "-reboot" ]; then
    ndmc -c 'opkg dns-override'
    sleep 3
    ndmc -c 'system configuration save'
    sleep 3
    echo "Перезагрузка роутера"
    ndmc -c 'system reboot'
fi


if [ "$1" = "-version" ]; then
    echo "Ваша версия KeenOS" "${keen_os_full}"
fi


if [ "$1" = "-help" ]; then
    echo "-install для установки"
    echo "-remove для удаления"
    echo "-update для обновления"
    echo "-version узнать версию KeenOS"
    #echo "-reinstall - use for reinstall all files script"
fi


if [ -z "$1" ]; then
    echo "-help посмотреть список доступных аргументов"
fi
