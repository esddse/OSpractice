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
RUN apt-get install -y expect

# 安装etcd
RUN apt-get install -y etcd

# 修改root密码
RUN echo "root:root" | chpasswd

# 创建共享目录，glusterfs的挂载点
RUN mkdir /root/shared

# 配置sshd，解除root的禁止登录，以及设置密钥读取的目录
RUN mkdir /var/run/sshd
RUN echo "AuthorizedKeysFile /root/shared/authorized_keys" >> /etc/ssh/sshd_config
RUN sed -n '/PermitRootLogin/d' /etc/ssh/sshd_config
RUN sed -n '/PubkeyAuthentication/d' /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config


# 复制初始程序
ADD init/ /root/init

# 开放22端口并前台运行jupyter
USER root
EXPOSE 22
WORKDIR /root
CMD ["python3","/root/init/init.py"]