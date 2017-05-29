# 作业报告
***

## 1. 阅读Paxos算法的材料并用自己的话简单叙述

参考[该博客](http://www.cnblogs.com/linbingdong/p/6253479.html)

#### 相关概念

在Paxos算法中，有三种角色:
* Proposer
* Acceptor
* Learner

在具体的实现中，一个进程可能同时充当多种角色。比如一个进程可能既是Proposer又是Acceptor又是Learner。

另外一个重要的概念提案（Proposal）。最重要达成一致的value就在提案里。

Proposer可以提出（propose）提案；Acceptor可以接受（accept）提案；如果某个提案被选定（chosen），那么该提案里的value就被选定了。如果Proposer、Acceptor、Learner都认为同一个value被选定（chosen），就称为“对某个数据达成一致”。

#### 问题描述

假设有一组可以提出（propose）value（value在提案Proposal里）的进程集合。一个一致性算法需要保证提出的这么多value中，只有一个value被选定（chosen）。如果没有value被提出，就不应该有value被选定。如果一个value被选定，那么所有进程都应该能学习（learn）到这个被选定的value。对于一致性算法，安全性（safaty）要求如下：
* 只有被提出的value才能被选定
* 只有一个value被选定，并且
* 如果某个进程认为某个value被选定，那么这个value必须是真的被选定的那个

不同角色之间可以通过发送消息来进行通信，消息在传递过程中可能出现任意时长的延迟，可能会重复，也可能丢失。但是消息不会被损坏，即消息内容不会被篡改

Paxos的目标：保证最终有一个value会被选定，当value被选定后，进程最终也能获取到被选定的value

#### Paxos算法描述

Paxos算法分为**两个阶段**，具体如下：

* 阶段一
	1. Proposer选择一个提案编号N，然后向半数以上的Acceptor发送编号为N的Prepare请求。
	2. 如果一个Acceptor收到一个编号为N的Prepare请求，且N大于该Acceptor已经响应过的所有Prepare请求的编号，那么它就会将它已经接受过的编号最大的提案（如果有的话）作为响应反馈给Proposer，同时该Acceptor承诺不再接受任何编号小于N的提案。 
* 阶段二
	1. 如果Proposer收到半数以上Acceptor对其发出的编号为N的Prepare请求的响应，那么它就会发送一个针对[N,V]提案的Accept请求给半数以上的Acceptor。注意：V就是收到的响应中编号最大的提案的value，如果响应中不包含任何提案，那么V就由Proposer自己决定。
	2. 如果Acceptor收到一个针对编号为N的提案的Accept请求，只要该Acceptor没有对编号大于N的Prepare请求做出过响应，它就接受该提案。

![Paxos算法](./pics/paxos_algorithm.PNG)

#### Learner学习被选定的value

Learner学习（获取）被选定的value有如下三种方案：

![paxos_learner](./pics/paxos_learner.PNG)


## 2. 模拟Raft协议工作的一个场景并叙述处理过程

参考[该博客](http://www.jdon.com/artichect/raft.html)

在Raft中，任何时候一个服务器可以扮演下面三种角色之一:
* Leader：处理所有客户端交互，日志复制等，一般一次只有一个Leader
* Follower: 类似选民，完全被动
* Candidate: 类似Proposer律师，可以被选为一个新的领导人

Raft阶段分为两个，首先是选举过程，然后在选举出来的领导人带领进行正常操作，比如日志复制等。

#### 选举

Raft使用心跳机制触发leader选举。当服务器启动时，它们一开始都是follower。follower只要能够接收到来自leader和candidate的信号，就能够一直保持follower状态。如果有一个follower未接收到信号的时间超过其election timeout，它会假定不存在leader，从而转换成cadidate开启新一轮选举。

candidate有权发起投票，它向其他服务器发起投票请求，并将将自己仅有的一票投给自己。其他服务器收到投票请求后，会给candidate投票。当candidate收到超过一半的投票后就成为leader。Raft系统中只有leader才有权利接收并处理client请求，并向其它服务器发出添加日志请求来提交日志。

#### 日志复制

leader选举出来以后，就可以开始处理客户端请求。leader收到client的请求后，将请求内容加入到自己的日志中，并向其他服务器发送添加日志请求。其它服务器收到添加日志请求后，判断该请求是否满足接收条件，若满足则将其加入到本地日志中，并发送response。leader受到大多数服务器添加成功的response后，就将那条日志正式提交。提交后的日志就意味着已经被Raft系统接受，并能应用到状态机中了。

## 3. 简述Mesos的容错机制并验证

[参考文章](http://www.infoq.com/cn/articles/analyse-mesos-part-03/)

Mesos可以在下列三个层面上实现容错:
* **Master**：Mesos使用热备份（hot-standby）设计来实现Master节点集合，一个Master结点与多个备用（standby）结点运行在同一集群中，并由开源软件Zookeeper来监控。Zookeeper会监控Master集群中所有的节点，并在Master节点发生故障时管理新Master的选举。当一个新的Master当选后，Zookeeper会通知Framework和选举后的Slave节点集合，以便使其在新的Master上注册。彼时，新的 Master可以根据Framework和Slave节点集合发送过来的信息，重建内部状态。
* **Framework Scheduler**：Framework调度器的容错是通过Framework将调度器注册2份或者更多份到Master来实现。当一个调度器发生故障时，Master会通知另一个调度来接管。需要注意的是Framework自身负责实现调度器之间共享状态的机制。
* **Slave**：Mesos实现了Slave的恢复功能，当Slave节点上的进程失败时，可以让执行器/任务继续运行，并为那个Slave进程重新连接那台Slave节点上运行的执行器/任务。当任务执行时，Slave会将任务的监测点元数据存入本地磁盘。如果Slave进程失败，任务会继续运行，当Master重新启动Slave进程后，因为此时没有可以响应的消息，所以重新启动的Slave进程会使用检查点数据来恢复状态，并重新与执行器/任务连接。

其中Framework Scheduler和Slave的错误是容易解决的，只要master检测到，并且执行相应处理程序即可。而Master的容错主要是通过Zookeeper模块执行的。在这里我们只验证Master失效的情况。

#### Zookeeper配置及Master宕机测试

在三台机器上修改``/etc/hosts``如下:

```
172.16.1.172  server-1
172.16.1.113  server-2
172.16.1.113  server-3
```

zookeeper在安装mesos时已经安装好，使用``locate``命令找到其配置文件路径为``/etc/zookeeper/conf/zoo.cfg``

在三台机器上修改其内容，加入三台虚拟机的hostname:

```
# specify all zookeeper servers
# The fist port is used by followers to connect to the leader
# The second one is used for leader election
server.1=server-1:2888:3888
server.2=server-2:2888:3888
server.3=server-3:2888:3888
```

根据配置文件中的数据地址,修改``/var/lib/zookeeper/myid``内容为上面对应的服务器号

在三台机器上启动zookeeper服务
```
/usr/share/zookeeper/bin/zkServer.sh start
```

查看状态，此时选举完毕，产生一个leader和两个follower
```
# server-1
root@oo-lab:/usr/share/zookeeper/bin# ./zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /etc/zookeeper/conf/zoo.cfg
Mode: leader

# server-2
root@oo-lab:/usr/share/zookeeper/bin# ./zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /etc/zookeeper/conf/zoo.cfg
Mode: follower

# server-3
root@oo-lab:/var/log/zookeeper# /usr/share/zookeeper/bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /etc/zookeeper/conf/zoo.cfg
Mode: follower
```

查看master.log可以发现选出``172.16.1.113``作为master
```
I0528 09:05:20.876953 21343 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.1.113:5060, log-replica(1)@172.16.1.157:5070, log-replica(1)@172.16.1.172:5050 }
I0528 09:05:20.879847 21342 contender.cpp:152] Joining the ZK group
I0528 09:05:20.880666 21340 master.cpp:2058] Successfully attached file '/var/log/mesos/mesos-master.INFO'
I0528 09:05:20.880704 21340 master.cpp:2137] The newly elected leader is master@172.16.1.113:5060 with id f89cbbb1-b50a-4865-87a9-25981be30b60
```

使用``kill``命令杀死master，造成宕机的效果。查看日志，新选出了``172.16.1.172``作为master。
```
I0528 09:38:14.466249  2100 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.1.157:5070, log-replica(1)@172.16.1.172:5050 }
I0528 09:38:14.471395  2099 zookeeper.cpp:259] A new leading master (UPID=master@172.16.1.172:5050) is detected
I0528 09:38:14.475183  2100 recover.cpp:197] Received a recover response from a replica in VOTING status
I0528 09:38:14.519208  2101 contender.cpp:152] Joining the ZK group
I0528 09:38:14.519604  2102 master.cpp:2058] Successfully attached file '/var/log/mesos/mesos-master.INFO'
I0528 09:38:14.519642  2102 master.cpp:2137] The newly elected leader is master@172.16.1.172:5050 with id 817de704-66e1-44be-a927-88865176e015
```

## 4. 综合作业：docker容器集群
