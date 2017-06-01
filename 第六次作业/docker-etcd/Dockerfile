FROM ubuntu:latest

# 安装ssh和jupyter
RUN apt-get update
RUN apt-get install -y ssh python3-pip
RUN pip3 install jupyter

# 安装一些工具
RUN apt-get install -y python3
RUN apt-get install -y net-tools
RUN apt-get install -y curl
RUN apt-get install -y vim
RUN apt update
RUN apt install sudo

# 安装etcd
RUN apt-get install -y etcd

# 创建ssh登录账号
RUN useradd -ms /bin/bash calico 
RUN adduser calico sudo
RUN echo "calico:calico" | chpasswd

# 修改root密码
RUN echo "root:root" | chpasswd

# 创建共享目录，glusterfs的挂载点
RUN mkdir /shared

# 配置sshd
RUN mkdir /var/run/sshd
RUN echo "AuthorizedKeysFile /home/calico/.ssh/authorized_keys" >> /etc/ssh/sshd_config



# 复制初始程序
ADD init/ /home/calico/init

# 开放22端口
USER calico
EXPOSE 22
WORKDIR /home/calico
CMD ["python3","/home/calico/init/init.py"]