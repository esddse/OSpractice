import os
import json
import time
import urllib
import subprocess
from urllib import request

while True:
	f = os.popen('echo "calico" | sudo -S bash -c "wc -l /shared/authorized_keys"')
	message = f.read().strip()
	if message[0] == '3':
		break