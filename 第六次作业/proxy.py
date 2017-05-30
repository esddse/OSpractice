import os
import sys
import json
import time
import urllib
import subprocess
from urllib import request

HOST_1 = '172.16.1.172'
HOST_2 = '172.16.1.113'
HOST_3 = '172.16.1.157'


def get_ip():
	f = os.popen("ifconfig ens32 | grep 'inet addr' | awk '{ print $2}' | awk -F: '{print $2}' ")
	return f.read().strip()

def master_in_(ip):
	jupyter_url = 'http://' + ip + ':8888/tree'
	request = urllib.request.Request(jupyter_url)
	try:
		f = urllib.request.urlopen(request)
	except:
		return False
	else:
		print('master running on ' + ip)
		return True

def set_proxy(ip1, ip2):
	args = ['configurable-http-proxy', 
			'--default-target=http://' + ip1 + ':8888', 
			'--ip=' + ip2, '--port=8888'] 
	return subprocess.Popen(args)

def loop_1(h_ip):
	last_pid = None
	last_master = -1
	while True:
		if master_in_(HOST_2):
			# first time
			if last_pid is None:
				last_pid = set_proxy(HOST_2, h_ip)
				last_master = HOST_2
			# not the first time
			elif last_master != HOST_2:
				last_pid.kill()
				last_pid = set_proxy(HOST_2, h_ip)
				last_master = HOST_2
		elif master_in_(HOST_3):
			# first time
			if last_pid is None:
				last_pid = set_proxy(HOST_3, h_ip)
				last_master = HOST_3
			# not the first time
			elif last_master != HOST_3:
				last_pid.kill()
				last_pid = set_proxy(HOST_3, h_ip)
				last_master = HOST_3
		elif last_pid is not None:
			last_pid.kill()
			last_pid = None
			last_master = -1

		time.sleep(3)


def loop_23(h_ip):
	last_pid = None
	last_master = -1
	have_master = False
	while True:
		# check every container
		for i in range(3):
			c_ip = '192.168.0.' + str(i+1)
			if master_in_(c_ip):
				have_master = True
				# first time
				if last_pid is None:
					last_pid = set_proxy(c_ip, h_ip)
					last_master = c_ip
				# not the first time 
				elif last_master != c_ip:
					last_pid.kill()
					last_pid = set_proxy(c_ip, h_ip)
					last_master = c_ip

		if not have_master and last_pid is not None:
			last_pid.kill()
			last_pid = None
			last_master = -1

		time.sleep(3)




def main():
	
	h_ip = get_ip()

	if h_ip == HOST_1:
		loop_1(h_ip)
	elif h_ip == HOST_2 or h_ip == HOST_3:
		loop_23(h_ip)


if __name__ == "__main__":
	main()