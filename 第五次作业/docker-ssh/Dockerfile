FROM ubuntu:latest

# 安装ssh
RUN apt-get update
RUN apt-get install -y ssh

# 创建账号用以登录
RUN useradd -m calico
RUN echo "calico:calico" | chpasswd

# 创建sshd使用的目录
RUN mkdir /var/run/sshd

# 开放22端口并用root前台运行sshd
USER root
EXPOSE 22
CMD ["/usr/sbin/sshd","-D"]