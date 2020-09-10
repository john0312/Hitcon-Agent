#!/bin/bash

ip addr add 192.168.122.22/24 dev ens3
ip route add default via 192.168.122.1

chmod 000 /bin/kill
chmod 000 /usr/bin/killall

if [[ -b /dev/sdc ]]; then
    if ! [[ -d "/var/www/html/storage.orig" ]]; then
        mv /var/www/html/storage /var/www/html/storage.orig
        mkdir /var/www/html/storage
    fi
    mount /dev/sdc /var/www/html/storage
    if ! [[ -f "/var/www/html/storage/index.html" ]]; then
        cp -pR /var/www/html/storage.orig/* /var/www/html/storage/.
    fi
fi

# Shameless path hardcoding.
su - -c "cd /hitcon; python3 ./guest_agent_main.py &"
