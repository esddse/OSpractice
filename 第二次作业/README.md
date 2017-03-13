# 作业报告
***
## 1. 用自己的语言描述Mesos的组成结构，指出它们在源码中的具体位置，简单描述一下它们的工作流程

#### Mesos组成架构

![mesos架构](./pics/mesos_arch.PNG)

上图比较简明扼要地展示了Mesos的主要组成部分。Mesos包括一个*master*守护进程，用来管理运行在各个集群结点上的*agent*守护进程，*Mesos frameworks*在这些agent之上运行各种任务。

master通过*resource offer*在框架间进行资源分配，这种机制使得细粒度的资源共享称为了可能。master会根据现有的分配组织策略（比如均等的分配策略或者有严格优先级的分配策略）来决定对各个框架分别offer多少资源。为了支持多种分配策略，master通过模块化架构和模块插入机制使其较为简单地实现。显然master可能会遇到单点故障的问题，Mesos通过Zookeeper解决该问题。它会维持一些预备的master结点，在当前master出现故障时由预备master通过“选举机制”选出新的master。

agent负责接受并执行来自master的命令，管理节点上的task。当agent上存在空闲的资源时，agent将自己的空闲资源量发送给master，再由master的分配。当task运行时，agent会将任务放到包含固定资源的container中运行，以达到资源隔离的效果。

在Mesos之上运行地framework包括两个组成部分：一个scheduler负责向master注册，以及接受或者拒绝master的资源offer；另一个executor运行在agent结点上，执行framework的任务。master决定配给一个framework多少资源，而该framework的scheduler选择到底用哪一个被分配的资源。当一个framework接受资源offer，它会将任务描述发送给Mesos，然后Mesos将这些任务在agent上启动。因此，整个Mesos系统是一个双层调度的框架：第一层由master将资源分配给框架；第二层由框架自己的调度器将资源分配给自己内部的任务。

在源代码中的位置如下
* master: [mesos-1.1.0/src/master](../mesos-1.1.0/mesos-1.1.0/src/master)
* agent(slave): [mesos-1.1.0/src/slave](../mesos-1.1.0/mesos-1.1.0/src/slave)
* framework-scheduler: [mesos-1.1.0/src/scheduler](../mesos-1.1.0/mesos-1.1.0/src/scheduler)
* framework-executer: [mesos-1.1.0/src/executer](../mesos-1.1.0/mesos-1.1.0/src/executer)

#### Mesos运行流程 (Resource offer 的流程)

Mesos的工作，即在不同的计算框架之间细粒度地分配资源（CPU、内存），主要是通过resource offer机制完成的。下图是一个很好的resource offer的例子:

![resource offer](./pics/resource_offer.PNG)

主要经过下面4个步骤:

1. Agent 1 向master报告它有4个CPU和4GB内存可用。于是master启用分配模块，得知framework 1 应该分配所有当前可用的资源。
2. master发送向framework 1 发送resource offer，告诉framework 1 在agent 1 上有哪些可用的资源。
3. framework 1 的scheduler发送信息回应master，描述了将要在agent上运行的两个任务，第一个任务需要2个CPU、1GB内存，第二个任务需要1个CPU、2GB内存。
4. 最终，master将任务发送给agent，并且分配相应的资源给framework的executer，然后executor就在agent上运行那两个任务。因为agnet 1 上还有1个CPU和1GB内存没有被分配，master的分配模块可能将其分配给framework 2.

值得一提的是，当master的资源offer无法满足framework的要求，framework可以拒绝该offer，并且等待直到一个满足要求的offer出现。



## 2. 用自己的语言描述框架（如Spark On Mesos）在Mesos上的运行过程，并与在传统操作系统上运行程序进行对比

在上题中，我主要以Mesos的视角说明了运行流程，本题则要求以框架的视角来说明。这里，我用Spark On Mesos作为例子来说明运行过程。Spark的架构如下图:

![spark](./pics/spark.PNG)

当Spark以Standalone模式运行时，中间的Cluster Manager是Spark自己的Standalone Cluster Manager,而运行在Mesos上，Cluster Manager变成了Mesos master来集中管理资源。SparkContext是Spark中用来管理和协调各个Spark进程的对象（在Driver Program中）。它会和master交互，一旦连接上master，Spark就获得了master分配的结点上的executor，executer可以用来为你的程序进行计算或者存储数据。然后SparkContext发送应用程序代码到各个executer结点上，最后发送Task到executer上运行。

结合1、2题，我将在Mesos上运行框架和在传统操作系统上运行程序的相同和不同总结如下：

* **相同：**
  1. Mesos和传统操作系统都向上层应用程序屏蔽抽象了底层硬件，只是提供接口供调用。
  2. 都有隔离机制。框架与框架之间，进程与进程之间一般互不影响，独立运行。

* **不同：**
  1. 底层硬件不同。Mesos管理集群，而传统操作系统针对单机。
  2. 运行的应用程序类型不同。Mesos上运行的程序大多是分布式的、高并行度的，而传统操作系统的应用程序大多是单机的、并行度低甚至是顺序执行的。结构上分布式框架多数需要使用master-slave模型进行控制；单机程序不需要这种模型。
  3. 同步程度和同步机制不同。Mesos运行的框架大多是异步执行任务的，仅仅在几个关键节点进行同步，同步的方法是进程间相互发送信息；而传统操作系统由于只有一个内存，同步变得尤为重要，同步的方法多是使用互斥锁。
  4. Mesos上运行分布式程序需要更多地考虑硬件失效的问题，随着结点数的增加，失效的概率会上升。Mesos专门设计了一套应对单点失效的机制，而传统的操作系统基本无需考虑这个问题。
  5. 对通信和IO的要求不同。Mesos上运行的分布式程序一般需要大量结点与结点间通信，对IO的速度有更大的需求。
  6. 程序与操作人员的交互目前在传统的操作系统上更为多样化。


## 3. 叙述master和slave的初始化过程

#### libprocess

libprocess是Mesos底层的一个基本库，它与Mesos各个部分的实现以及通信息息相关，因为它是整个结构的基础，在这里先简要介绍其作用与思想。

libprocess是基于[actor模型](https://en.wikipedia.org/wiki/Actor_model)实现的。在actor模型中，所有东西都被视为一个actor。actor之间是独立的，它们的交互只能通过相互发送信息，actor可以通过得到的信息作出反应。一般来说，actor可以维护一个消息队列，顺序地接收消息。在libprocess里，类似actor的执行任务的单元叫做process，每一个process有一个独立的ID。process之间只要直到对方ID，就能进行异步通信。

在Mesos的master结点中，每个framework和agent都是一个远程的process。而在agent结点上，每个executer也是一个process。

Mesos里面的消息传递是通过libprocess + protocol buffer来实现的。其流程图如下：

![消息传递接收](./pics/libprocess.jpg)

#### Master

master目录中和初始化流程有关的文件是[main.cpp](../mesos-1.1.0/mesos-1.1.0/src/master/main.cpp)[master.hpp](../mesos-1.1.0/mesos-1.1.0/src/master.master.hpp)和[master.cpp](../mesos-1.1.0/mesos-1.1.0/src/master/master.cpp)。

在main.cpp中，先是进行了一些配置工作，比如设定ip、端口、防火墙等，在一系列配置之后，在最后终于创建了一个master实例:

```
Master* master =
	  new Master(
      	allocator.get(),
      	registrar,
      	&files,
      	contender,
      	detector,
      	authorizer_,
      	slaveRemovalLimiter,
      	flags);
```
创建完后为了真正让其运行起来，还需要产生一个独立的process。并且创建完毕后等待master进程结束。这里的process就是在上文中说到的libprocess中定义的process，而不是简单的进程。
```
process::spawn(master);
process::wait(master->self());
```

在master.hpp中定义了master的基本功能和数据结构


#### Slave (Agent)


## 4. 查找资料，简述Mesos的资源调度算法，指出在源代码中的具体位置并阅读，说说你对它的看法

## 5. 写一个完成简单工作的框架(语言自选，需要同时实现scheduler和executor)并在Mesos上运行，在报告中对源码进行说明并附上源码，本次作业分数50%在于本项的完成情况、创意与实用程度。（后面的参考资料一定要读，降低大量难度）
