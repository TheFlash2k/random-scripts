#!/bin/bash

# But this shit slow AF

if [[ $# != 1 ]]; then
	echo "No arguments provided! Please provided an ip. (192.168.10.0)"
	exit
fi

begin=100
end=254

ip=$1
# Extracting the ip:
IFS='.' read -a ip_arr <<< $ip
ip="${ip_arr[0]}.${ip_arr[1]}.${ip_arr[2]}"

for i in $(seq $begin $end); do
	cmd_ping=`ping $ip.$i -c 1`
	last_exec=$?
	echo -n "$ip.$i: "
	if [[ $last_exec == 1 ]]; then 
			echo "Closed"
			((closed=closed+1))

	elif [[ $last_exec == 0 ]]; then
		echo -n "Open : "
		box=`echo $cmd_ping | cut -d ' ' -f 13 | cut -d '=' -f 2`
		if [[ $box == "64" ]]; then
			echo "Unix (Maybe linux)"
		elif [[ $box == "128" ]]; then
			echo "Windows"
		else
			echo "Undefined OS"
		fi
	else
		echo "Undefined"
	fi
done
