import os
import json
import time
import urllib
import subprocess
from urllib import request



f = os.popen('etcdctl ls --recursive /etcd')
lines = f.read().strip().split('\n')

if not lines[0].startswith('/etcd'):
	with open('/etc/hosts', 'w') as f:
		f.write('127.0.0.1  localhost\n')
	exit() 

dic = {}

for line in lines:
	line = line.split('/')
	if len(line) == 3:
		f = os.popen('etcdctl get ' + '/'.join(line))
		role = f.read().strip()
		dic[line[2]] = role
	
dic = sorted(dic.items(), key=lambda item: item[0][-1])

with open('/etc/hosts', 'w') as f:
	f.write('127.0.0.1  localhost\n')
	cnt = 1
	for item in dic:
		ip = item[0]
		role = item[1]
		if role == 'master':
			f.write(ip + ' etcd-0\n')
		else:
			f.write(ip + ' etcd-' + str(cnt) + '\n')
			cnt += 1

