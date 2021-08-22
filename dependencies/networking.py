#!/usr/bin/env python3

from sys import stderr

# Variable definition:
MAX_LEN = 256

def get_cidr_mask(subnet: str):

	subnet = [int(i) for i in subnet.split('.')]
	binary_subnet = list()

	for i in subnet:
		bin_num = bin(i).replace("0b", '')
		binary_subnet.append(bin_num)

	cidr_mask = 0

	for octet in binary_subnet:
		if octet == '1' * 8:
			cidr_mask += 8

		else:
			for num in octet:
				if num == '1':
					cidr_mask += 1

	return cidr_mask

def get_network_portion(ip : str, subnet : str):

	ip = [int(i) for i in ip.split('.')]
	subnet = [int(i) for i in subnet.split('.')]
	
	network = list()

	for i in range(len(ip)):
		portion = ip[i] & subnet[i]
		network.append(str(portion))

	return '.'.join(network)
def get_network_portion_from_cidr_mask(ip: str, cidr_mask : int, binary=False):

	if cidr_mask > 32:
		print("[-] Invalid cidr mask...", file=stderr)
		return

	# Firstly creating the subnet mask from that specific cidr mask
	full_portions = int(cidr_mask / 8)
	subnet = list()

	for i in range(full_portions):
		subnet.append('1' * 8)

	rem_portion = cidr_mask - (8 * full_portions)


	if rem_portion <= 8 and rem_portion != 0:
		curr_mask = '1' * rem_portion + '0' * (8 - rem_portion)
		subnet.append(curr_mask)

	while len(subnet) <= 4:
		subnet.append('0' * 8)

	# In case 32 is entered, a trailing 0 is added.
	while len(subnet) > 4:
		subnet.pop()

	if not binary:
		subnet = [str(int(i, 2)) for i in subnet]

	return '.'.join(subnet)
def get_host_portion(ip : str, subnet : str):
	
	subnet_portion = [bin(int(i)).replace('0b', '') for i in subnet.split('.')]
	ip = [int(i) for i in ip.split('.')]

	host_portion = list()

	for i in range(len(subnet_portion)):

		host_port = ""

		if len(subnet_portion[i]) != 8:
			subnet_portion[i] = subnet_portion[i] + ('0' * (8 - len(subnet_portion[i])))

		for j in range(len(subnet_portion[i])):
			host_port += '1' if subnet_portion[i][j] == '0' else '0'
		host_portion.append(int(host_port, 2))

	host_portion = [str(host_portion[i] & int(ip[i])) for i in range(len(host_portion))]
	return '.'.join(host_portion)

# Returns an IP in its binary form:
def ip_to_bin(ip : str):
	bin_ip = ""

	ip = ip.split('.')
	ip = [bin(int(i)).replace('0b','') for i in ip]
	# Setting the length of each index to 8:
	for i in range(len(ip)):
		while len(ip[i]) < 8:
			ip[i] += '0'

	return '.'.join(ip)
def bin_to_ip(bin_ip : str):
	return '.'.join([str(int(ip, 2)) for ip in bin_ip.split('.')])
def get_number_of_ips(host_portion : str):
	num = -2 # As we have to remove the network portion as well as the broadcast address.
	
	ips = host_portion.split('.')
	original_host = host_portion.split('.')

	# Checking if host portion is > '255.255.255.0':
	int_ips = [int(i) for i in ips]
	sum_addr = sum(int_ips)
	if sum_addr > 765: # 255 + 255 + 255 + 0
		host = int(host_portion.split('.')[-1])
		return 254 - host

	# Getting the values for the remaining subnets: except /16 and /8
	elif sum_addr < 510 and sum_addr != 255:
		# Getting all the non zero portions in a list
		# Check which of them are not = 256.
		# If its 255, add 1 to them
		# if not, subtract them from 256
		# Multiply all the values
		non_zeros = list()
		for i in int_ips:
			if i != 0:
				if i != 255:
					i = (256 - i)
					non_zeros.append(i)
			elif i == 0:
				non_zeros.append(256)
		
		t_num_ip = 1
		for i in non_zeros:
			t_num_ip *= i
		# We have to -2 because of the network address and the broadcast address
		return (t_num_ip - 2)
		

	# Hard coding value for /16 subnet
	elif sum_addr == 510:
		return 65534

	# Hard coding value for /8 subnet:
	elif sum_addr == 255:
		return 16777214


	i = 0
	part = 0
	while i != 4:
		if ips[i] == '0':
			ips[i] = '255'
			i += 1
			continue
		if ips[i] != '255':
			part = i
			ips[i] = str(int(ips[i]) + 1)
			continue
		i += 1

	# This will actually identify the portion that isn't 255 like 192 in a /18 subnet.
	val = int(original_host[part])
	# That portion subtracted from the max value i.e. of 256
	rem_port = MAX_LEN - val

	while part != len(ips):
		# I have no idea.
		# i suck lpc
		if part == 0:
			num = 254
			break
		part += 1
		if part >= len(ips):
			break
		num += (int(ips[part]) + 1) * rem_port

	return num
def add_bit_to_ip(ip : str):
	ip = ip.split('.')
	for i in range(len(ip)):
		if ip[i] != '255':
			ip[i] = str(int(ip[i]) + 1)
			return '.'.join(ip)

def is_valid_ip(ip : str) -> bool:
	from re import match
	return bool(match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip))

def subnet_to_ips(ip : str, subnet_mask : int, err = True) -> list:

	if subnet_mask < 0 or subnet_mask > 32:
		print("[-] Invalid subnet mask provided!", file=stderr)
		exit()

	elif subnet_mask == 31 or subnet_mask == 32:
		print(f"[x] There are no usable ip(s) in /{subnet_mask} mask!", file=stderr)
		exit()

	# Will be returned and will contain all the ips:
	ret_ips = list()
	ips = ip.split('.')

	host_portion = get_network_portion_from_cidr_mask(ip, subnet_mask)
	num_ips = get_number_of_ips(host_portion)

	# Finding the first zero in the list as the network address always contains a zero:
	if '.0.' not in ip and '.0' != ip[len(ip) - 2:]:
		if err:
			print(f"[-] Invalid IP for network address provided! Please provide a valid ip.", file=stderr)
			print(f"[*] Trying to resolve network address. False IPs which might not be in the subnet may be generated...", file=stderr)
		else:
			print("",end="") # The best way to do nothing xDDDDD

	# Checking if the host portion and the ip contains the same number of zeros:
	num_zeroes_host = 0
	num_zeroes_ip = 0

	for i in host_portion.split():
		if i == '0':
			num_zeroes_host += 1

	for i in ip.split():
		if i == '0':
			num_zeroes_ip += 1

	# If they do not match, then we'll find the first 0 in host portion,
	# starting at that index, we'll set everything afterwards in the ip
	# to 0 so that we'll start from the network address.
	if num_zeroes_host != num_zeroes_ip:
		# Finding the first zero in host:
		for i in host_portion.split():
			if i == '0':
				break
		ip = ip.split('.')
		for j in range(i, len(ip)):
			ip[j] = '0'

	last_pos = 0
	# Identifying the last portion at which '0' exists:
	for i in range(len(ips)):
		if i == '0':
			last_pos = i

	copy_ips = ip.split('.')

	if i != len(ips) - 1:
		print(f"[-] Invalid IP for network address provided! Please provide a valid ip.", file=stderr)
		return None
	else:
		# Checking the num of ips is less than 254, that would mean that we would have to simply have to
		# add the ips to the range and just return:
		if num_ips <= 254:
			for j in range(1, num_ips + 1):
				copy_ips[3] = str(j)
				ret_ips.append('.'.join(copy_ips))
		else:
			for j in range(1, num_ips + 1):
				overflow = False
				iter = j % 256
				if copy_ips[3] == '255':
					if copy_ips[2] != '255':
						copy_ips[2] = str(int(copy_ips[2]) + 1)
						if copy_ips[2] != ips[2]:
							copy_ips[3] = '0'
					elif copy_ips[1] != '255':
						copy_ips[1] = str(int(copy_ips[1]) + 1)
						if copy_ips[1] != ips[1]:
							copy_ips[2] = '0'
							copy_ips[3] = '0'
					elif copy_ips[0] != '255':
						copy_ips[0] = str(int(copy_ips[0]) + 1)
						if copy_ips[0] != ips[0]:
							copy_ips[1] = '0'
							copy_ips[2] = '0'
							copy_ips[3] = '0'
				else:
					copy_ips[3] = str(iter)
				ret_ips.append('.'.join(copy_ips))
	

	return ret_ips

'''
if __name__ == "__main__":
	# Finding the network portion
	ip = "192.168.33.12"
	subnet = "255.255.224.0"
	network_portion = get_network_portion(ip=ip, subnet=subnet)

	# Can also work like this.
	# data = "192.168.33.12/255.255.224.0"
	# data = data.split('/')
	# network_portion = get_network_portion(ip=data[0], subnet=data[1])
	
	# Finding the cidr mask from a certain subnet
	subnet_mask = get_cidr_mask(subnet)

	# Finding the network portion from a certain cidr mask
	ip = "192.168.33.12"
	cidr = 19
	subnet = get_network_portion_from_cidr_mask(ip=ip, cidr_mask=cidr)

	print(subnet)

	# Can also work like this:
	# data = "192.168.33.12/19"
	# data = data.split('/')
	# subnet = get_network_portion_from_cidr_mask(ip=data[0], cidr_mask=int(data[1]))

	# Finding the host portion in a network:
	# host_portion = get_host_portion(ip=ip, subnet=subnet)
	# print(host_portion)

	# Finding the total number of usable ips:
	host_portion = get_network_portion_from_cidr_mask(ip, subnet_mask)
	num_ips = get_number_of_ips(host_portion)
	print(f"Number of usable ips: {num_ips}")

	# Find all the *usable* ips in a subnet:
	ip = "172.0.0.0"
	subnet_mask = 15
	ips = subnet_to_ips(ip, subnet_mask)
	print(f"Following {len(ips)} are usable:")
	for ip in ips:
		print(ip)

'''
