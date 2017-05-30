import os
import json
import time
import urllib
import subprocess
from urllib import request


def main():
	f = os.popen('etcdctl ls --recursive /etcd')
	lines = f.read().strip().split('\n')

	with open('/etc/hosts', 'w') as f:
		f.write('127.0.0.1  localhost\n')
		cnt = 1
		for line in lines:
			line = line.split('/')
			if len(line) == 4 and line[2] == 'master':
				f.write(line[3] + ' etcd-0\n')
			elif len(line) == 4 and line[2] == 'slave': 
				f.write(line[3] + ' etcd-' + str(cnt) + '\n')
				cnt += 1


if __name__ == "__main__":
	main()