#!/bin/bash

if [[ $# != 1 ]]; then
  echo "[-] No interface provided!"
  exit
fi

# Al it does is just simply requests a new ip from the DHCP server (My ubuntu doesn't do it automatically :( )

ip link set $1 up
dhclient $1 -v
