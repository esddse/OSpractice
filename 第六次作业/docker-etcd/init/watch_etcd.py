import os
import json
import time
import urllib
import subprocess
from urllib import request

last_txt = None
while True:
	f = os.popen('etcdctl ls --recursive /etcd')
	txt = f.read().strip()

	if last_txt != txt:
		args = ['python3', '/root/init/edit_hosts.py']
		subprocess.Popen(args)
		last_txt = txt
		time.sleep(1)

	time.sleep(5)