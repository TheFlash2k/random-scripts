#!/usr/bin/env python3

from platform import system
from queue import Queue
import subprocess
from sys import argv
from threading import Thread, Lock
from dependencies.networking import *

# Encapsulating all our pinger functionality in a singleton.
class Pinger:
	# Might later add a functionality to print the OS based on TTLs
	ttl_table = {
			64 : "*nix (Linux/Unix)",
			128 : "Windows",
			254 : "Solaris/AIX",
			255 : 'FREEBSD/NETBSD/BSDI/SunOS'
	}

	@staticmethod
	def ping(host : str):

		if system().lower() == 'windows':
			param = 'n'
			cmd = 'ping'
			# tmp_file = '%tmp%\\tmp.txt' # (Maybe to store the output and then read it? But a race condition might occur)
		else:
			param = '-c'
			cmd = '/usr/bin/ping'
			# tmp_file = '/tmp/ping.txt'

		command = [cmd, param, '1', host]

		return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0

class Handler:

	def __init__(self, ips : list, num_threads = 200):
		self.total_threads = num_threads
		self.ips = ips
		self.ip_queue = Queue()
		self.mutex = Lock()
		self.curr_iter = 0
	
	# Private method (no private keyword in python) :(
	def __ping__(self, ip):
		with self.mutex:
			print(f"[*] Current IP : {ip}\r", end='')
		response = Pinger.ping(ip)
		if response:
			print(f"[+] {ip} is UP", end=' ' * 10)
			print()

	# Private method (no private keyword in python) :(
	def __worker__(self):
		while True:
			ip = self.ip_queue.get()
			self.__ping__(ip)
			self.ip_queue.task_done()

	def init(self):
		
		threads = list()

		for thread in range(self.total_threads):
			thread = Thread(target=self.__worker__)
			thread.daemon = True
			threads.append(thread)
			thread.start()

		# Enqueing each ip.
		for ip in self.ips:
			self.ip_queue.put(ip)

		for thread in threads:
			thread.join()

def usage():
	print(f"Usage: python3 {argv[0]} IP/mask\nExample: {argv[0]} 192.168.10.0/24")

def err(msg : str):
		print(msg, file=stderr)
		usage()
		exit(1)

def check_args():

	if len(argv) != 2:
		err("[-] Invalid number of arguments provided.")

	if argv[1] == 'h' or argv[1] == 'help':
		usage()
		exit(0)

	invalid_chars = (' ', '\'', '\\', '^', '<', '>', '|', '&', ';', ':')

	for char in invalid_chars:
		if char in argv[1]:
			err("[-] Invalid characters entered!")

	if '/' not in argv[1]:
		err("[-] Invalid format for data.")

	data = argv[1].split('/')

	subnet_mask = 0
	ip = ""

	# Checking subnet
	try:
		subnet_mask = int(data[1])
	except ValueError:
		err("[-] Invalid value for Mask provided!")

	import re
	ip = data[0]
	if not is_valid_ip(ip):
		err("[-] Invalid IP Address provided!")

	return ip, subnet_mask

if __name__ == "__main__":

	# ip = "192.168.0.100"
	# subnet_mask = 24

	ip, subnet_mask = check_args()

	ips = subnet_to_ips(ip, subnet_mask, err=False)

	ping = Handler(ips=ips, num_threads=200)
	
	print("[*] Note : If the program seems stuck, that means all the ips have been matched and the ones alive have been displayed.\nSo, to quit, just press CTRL + C\n")

	try:
		ping.init()
	except KeyboardInterrupt:
		print()
		exit(1)
