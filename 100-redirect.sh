#!/bin/sh

[ "$type" = "ip6tables" ] && exit 0
[ "$table" != "mangle" ] && [ "$table" != "nat" ] && exit 0

ip4t() {
    if ! iptables -C "$@" &>/dev/null; then
        iptables -A "$@" || exit 0
    fi
}

local_ip=$(ip -4 addr show br0 | awk '/inet/ {print $2}' | cut -d/ -f1)

for protocol in udp tcp; do
    if [ -z "$(iptables-save 2>/dev/null | grep "$protocol --dport 53 -j DNAT")" ]; then
        iptables -I PREROUTING -w -t nat -p "$protocol" --dport 53 -j DNAT --to "$local_ip"
    fi
done

if [ -z "$(iptables-save 2>/dev/null | grep unblocksh)" ]; then
    ipset create unblocksh hash:net -exist 2>/dev/null
	
    # Для работы на всех интерфейсах (br0, br1, sstp0, sstp2, etc)
    iptables -I PREROUTING -w -t nat -p tcp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082
    iptables -I PREROUTING -w -t nat -p udp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082

    # Если у вас другой конфиг dnsmasq, и вы слушаете только определенный ip, раскоментируйте следующие строки, поставьте свой ip
    #iptables -I PREROUTING -w -t nat -p tcp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1
    #iptables -I PREROUTING -w -t nat -p udp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1

    # Если вы хотите что бы обход работал только для определнных интерфейсов, закоментируйте строки выше, и раскоментируйте эти (br0)
    #iptables -I PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082
    #iptables -I PREROUTING -w -t nat -i br0 -p udp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082
    #iptables -I PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1
    #iptables -I PREROUTING -w -t nat -i br0 -p udp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1

    # Если вы хотите что бы обход работал только для определённых интерфейсов, закоментируйте строки выше, и раскоментируйте эти (sstp0)
    #iptables -I PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082
    #iptables -I PREROUTING -w -t nat -i sstp0 -p udp -m set --match-set unblocksh dst -j REDIRECT --to-port 1082
    #iptables -I PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1
    #iptables -I PREROUTING -w -t nat -i sstp0 -p udp -m set --match-set unblocksh dst --dport 53 -j DNAT --to 192.168.1.1
fi

if [ -z "$(iptables-save 2>/dev/null | grep unblocktor)" ]; then
    ipset create unblocktor hash:net -exist 2>/dev/null
    iptables -I PREROUTING -w -t nat -p tcp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
    iptables -I PREROUTING -w -t nat -p udp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
	
    #iptables -I PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
    #iptables -I PREROUTING -w -t nat -i br0 -p udp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
    #iptables -A PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
	
    #iptables -I PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
    #iptables -I PREROUTING -w -t nat -i sstp0 -p udp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
    #iptables -A PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocktor dst -j REDIRECT --to-port 9141
fi

if [ -z "$(iptables-save 2>/dev/null | grep unblockvless)" ]; then
    ipset create unblockvless hash:net -exist 2>/dev/null
    iptables -I PREROUTING -w -t nat -p tcp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
    iptables -I PREROUTING -w -t nat -p udp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
	
    #iptables -I PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
    #iptables -I PREROUTING -w -t nat -i br0 -p udp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
    #iptables -A PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
	
    #iptables -I PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
    #iptables -I PREROUTING -w -t nat -i sstp0 -p udp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
    #iptables -A PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblockvless dst -j REDIRECT --to-port 10810
fi

if [ -z "$(iptables-save 2>/dev/null | grep unblocktroj)" ]; then
    ipset create unblocktroj hash:net -exist 2>/dev/null
    iptables -I PREROUTING -w -t nat -p tcp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
    iptables -I PREROUTING -w -t nat -p udp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
	
    #iptables -I PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
    #iptables -I PREROUTING -w -t nat -i br0 -p udp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
    #iptables -A PREROUTING -w -t nat -i br0 -p tcp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
	
    #iptables -I PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
    #iptables -I PREROUTING -w -t nat -i sstp0 -p udp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
    #iptables -A PREROUTING -w -t nat -i sstp0 -p tcp -m set --match-set unblocktroj dst -j REDIRECT --to-port 10829
fi

TAG="100-redirect.sh"

if ls -d /opt/etc/unblock/vpn-*.txt >/dev/null 2>&1; then
    for vpn_file_name in /opt/etc/unblock/vpn*; do
        vpn_unblock_name=$(echo $vpn_file_name | awk -F '/' '{print $5}' | sed 's/.txt//')
        unblockvpn=$(echo unblock"$vpn_unblock_name")

        vpn_type=$(echo "$unblockvpn" | sed 's/-/ /g' | awk '{print $NF}')
        vpn_link_up=$(curl -s localhost:79/rci/show/interface/"$vpn_type"/link | tr -d '"')
        if [ "$vpn_link_up" = "up" ]; then
            vpn_type_lower=$(echo "$vpn_type" | tr [:upper:] [:lower:])
            get_vpn_fwmark_id=$(grep "$vpn_type_lower" /opt/etc/iproute2/rt_tables | awk '{print $1}')

            if [ -n "${get_vpn_fwmark_id}" ]; then
                vpn_table_id=$get_vpn_fwmark_id
            else
                break
            fi
            vpn_mark_id=$(echo 0xd"$vpn_table_id")

            if iptables-save 2>/dev/null | grep -q "$unblockvpn"; then
                vpn_rule_ok=$(echo Правила для "$unblockvpn" уже есть.)
                echo "$vpn_rule_ok"
            else
                info_vpn_rule=$(echo ipset: "$unblockvpn", mark_id: "$vpn_mark_id")
                logger -t "$TAG" "$info_vpn_rule"

                ipset create "$unblockvpn" hash:net -exist 2>/dev/null

                fastnat=$(curl -s localhost:79/rci/show/version | grep ppe)
                software=$(curl -s localhost:79/rci/show/rc/p lobes | grep software -C1  | head -1 | awk '{print $2}' | tr -d ",")
                hardware=$(curl -s localhost:79/rci/show/rc/ppe | grep hardware -C1  | head -1 | awk '{print $2}' | tr -d ",")
                if [ -z "$fastnat" ] && [ "$software" = "false" ] && [ "$hardware" = "false" ]; then
                    info=$(echo "VPN: fastnat, swnat и hwnat ВЫКЛЮЧЕНЫ, правила добавлены")
                    logger -t "$TAG" "$info"
                    iptables -A PREROUTING -w -t mangle -p tcp -m set --match-set "$unblockvpn" dst -j MARK --set-mark "$vpn_mark_id"
                    iptables -A PREROUTING -w -t mangle -p udp -m set --match-set "$unblockvpn" dst -j MARK --set-mark "$vpn_mark_id"

                    # Закоментируйте правила выше и раскоментируйте эти, если хотите перенаправлять трафик только с интерфейса br0
                    #iptables -I PREROUTING -w -t mangle -i br0 -p tcp -m set --match-set "$unblockvpn" dst -j MARK --set-mark "$vpn_mark_id"
                    #iptables -I PREROUTING -w -t mangle -i br0 -p udp -m set --match-set "$unblockvpn" dst -j MARK --set-mark "$vpn_mark_id"
                else
                    info=$(echo "VPN: fastnat, swnat и hwnat ВКЛЮЧЕНЫ, правила добавлены")
                    logger -t "$TAG" "$info"
                    iptables -A PREROUTING -w -t mangle -m conntrack --ctstate NEW -m set --match-set "$unblockvpn" dst -j CONNMARK --set-mark "$vpn_mark_id"
                    iptables -A PREROUTING -w -t mangle -j CONNMARK --restore-mark
                fi
            fi
        fi
    done
fi

exit 0
