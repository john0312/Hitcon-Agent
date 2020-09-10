#!/bin/bash

ip addr add 192.168.122.5/24 dev ens3
ip route add default via 192.168.122.1

# Shameless path hardcoding.
cd /hitcon
python3 ./guest_agent_main.py &
