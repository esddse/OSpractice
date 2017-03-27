# 作业报告
***

## 1. 安装配置Docker
跟随[官网教程](https://store.docker.com/editions/community/docker-ce-server-ubuntu?tab=description)，安装步骤如下：

1. 添加软件源

```
sudo apt-get -y install apt-transport-https ca-certificates curl
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
2. 下载 Docker CE
```
sudo apt-get -y install docker-ce
```
3. 测试 Docker CE 是否正确安装
```
sudo docker run hello-world
```

