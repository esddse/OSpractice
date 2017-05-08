FROM ubuntu:latest

# 安装ssh和jupyter
RUN apt-get update
RUN apt-get install -y ssh python3-pip
RUN pip3 install jupyter

# 创建账号用以登录
RUN useradd -m calico
RUN echo "calico:calico" | chpasswd

# 创建sshd使用的目录
RUN mkdir /var/run/sshd

# 开放22端口并前台运行jupyter
USER calico
EXPOSE 22
WORKDIR /home/calico
CMD ["jupyter","notebook","--NotebookApp.token=","--ip=192.168.0.1"]