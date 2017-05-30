import os
import json
import time
import urllib
import subprocess
from urllib import request

def init_etcd(ip):
	args = ['etcd',
		    '--name','container' + ip[-1],
		    '--initial-advertise-peer-urls', 'http://' + ip + ':2380',
		    '--listen-peer-urls', 'http://' + ip + ':2380',
		    '--listen-client-urls', 'http://' + ip + ':2379,http://127.0.0.1:2379',
		    '--advertise-client-urls', 'http://' + ip + ':2379',
		    '--initial-cluster-token', 'etcd',
		    '--initial-cluster', 'container1=http://192.168.0.1:2380,container2=http://192.168.0.2:2380,container3=http://192.168.0.3:2380',
		    '--initial-cluster-state', 'new',
		    ]
	subprocess.Popen(args)

def get_ip():
	f = os.popen("ifconfig cali0 | grep 'inet addr' | awk '{ print $2}' | awk -F: '{print $2}' ")
	return f.read().strip()

def gen_ssh_key(ip):
	os.system("ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa")
	os.system("touch /root/shared/"+ip)
	os.system("cat /root/.ssh/id_rsa.pub >> /root/shared/authorized_keys")
	os.system("chmod 600 /root/shared/authorized_keys")
	os.system("service ssh start")

def launch_jupyter(ip):
	args = ['jupyter', 'notebook', '--allow-root', '--NotebookApp.token=', '--ip='+ip]
	subprocess.Popen(args)


def init_watcher():
	args = ['etcdctl', 'exec-watch', '--recursive', '/etcd', '--', 'python3', '/root/init/edit_hosts.py']
	subprocess.Popen(args)

def etcd_loop(ip):
	etcd_self_url = "http://" + ip + ":2379/v2/stats/self"
	r = urllib.request.Request(etcd_self_url)
	is_master = False
	while True:
		try:
			f = urllib.request.urlopen(r)
		except:
			print('bad request: ' + etcd_self_url)
		else:
			s = json.loads(f.read().decode('utf8'))
		
			if s['state'] == 'StateLeader':
				if not is_master:
					launch_jupyter(ip)
					os.system('etcdctl rm /etcd')
					os.system('etcdctl mk /etcd/master/' + ip + ' ' + ip)
					is_master = True
				else:
					os.system('etcdctl mk /etcd/master/' + ip + ' ' + ip)
			else:
				is_master = False
				os.system('etcdctl mk /etcd/slave/' + ip + ' ' + ip)

		time.sleep(1)

def main():
	# 得到容器ip
	ip = get_ip()
	# 初始化etcd
	init_etcd(ip)
	# 产生密钥
	gen_ssh_key(ip)
	# 初始化etcd监视者
	init_watcher()
	# 循环，检查自身状态，写入etcd
	etcd_loop(ip)
	
	

if __name__ == "__main__":
	main()
	