
import re
import sys
import uuid
import logging
import time
import socket
import signal
import getpass
import subprocess
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data, decode_data
from addict import Dict

TASK_CPU = 0.1
TASK_MEM = 96
TASK_NUM = 10

EXECUTOR_CPUS = 0.2
EXECUTOR_MEM = 192

AGENT_1 = '6293002e-35cc-4827-a62b-b0412bb5218c-S0'
AGENT_2 = '6293002e-35cc-4827-a62b-b0412bb5218c-S1'

class MyScheduler(Scheduler):

    def __init__(self):
        self.task_launched = 0


    # invoked when resources have been offered to this framework
    def resourceOffers(self, driver, offers):
        filters = {'refuse_seconds': 5}

        # if all tasks have been launched, return directly 
        if self.task_launched == TASK_NUM:
            return 

        # for every offer
        for offer in offers:
            if self.task_launched == TASK_NUM:
                return 
            print(self.task_launched)
            # check if the offer satisfy the requirments
            cpus = self.getResource(offer.resources, 'cpus')
            mem = self.getResource(offer.resources, 'mem')
            if cpus < TASK_CPU or mem < TASK_MEM:
                continue

            # the 1st task to launch jupyter
            if self.task_launched == 0:
                # get agent_id
                agent_id = offer.agent_id.value

                
                # set proxy
                if agent_id == AGENT_1:
                    subprocess.Popen(['/usr/local/bin/configurable-http-proxy',
                                      '--default-target=http://172.16.1.113:8888',
                                      '--ip=172.16.1.172',
                                      '--port=8888'])
                else:
                    subprocess.Popen(['/usr/local/bin/configurable-http-proxy',
                                      '--default-target=http://172.16.1.157:8888',
                                      '--ip=172.16.1.172',
                                      '--port=8888'])
                
                # config a new task

                # network
                networkInfo = Dict()
                networkInfo.name = 'calico_test_net'

                # ip
                ip = Dict()
                ip.key = 'ip'
                ip.value = '192.168.0.1'

                # docker
                dockerInfo = Dict()
                dockerInfo.image = 'esddse/docker-jupyter'
                dockerInfo.network = 'USER'
                dockerInfo.parameters = [ip]

                # container
                containerInfo = Dict()
                containerInfo.type = 'DOCKER'
                containerInfo.docker = dockerInfo
                containerInfo.network_infos = [networkInfo]

                # task
                commandInfo = Dict()
                commandInfo.shell = False

                task = Dict()
                task_id = str(self.task_launched+1)
                task.task_id.value = task_id
                task.agent_id.value = offer.agent_id.value
                task.name = 'jupyter'
                task.container = containerInfo
                task.command = commandInfo

                task.resources = [
                    dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                    dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
                ]

            else:
                # config a new task

                # network
                networkInfo = Dict()
                networkInfo.name = 'calico_test_net'

                # ip
                ip = Dict()
                ip.key = 'ip'
                ip.value = '192.168.0.' + str(self.task_launched+1)

                # docker
                dockerInfo = Dict()
                dockerInfo.image = 'esddse/docker-ssh'
                dockerInfo.network = 'USER'
                dockerInfo.parameters = [ip]

                # container
                containerInfo = Dict()
                containerInfo.type = 'DOCKER'
                containerInfo.docker = dockerInfo
                containerInfo.network_infos = [networkInfo]

                # task
                commandInfo = Dict()
                commandInfo.shell = False

                task = Dict()
                task_id = str(self.task_launched+1)
                task.task_id.value = task_id
                task.agent_id.value = offer.agent_id.value
                task.name = 'ssh'
                task.container = containerInfo
                task.command = commandInfo

                task.resources = [
                    dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                    dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
                ]
                

            # launch task
            driver.launchTasks(offer.id, [task], filters)

            self.task_launched += 1


    def getResource(self, res, name):
        for r in res:
            if r.name == name:
                return r.scalar.value
        return 0.0

    # invoked when the status of a task has changed
    # eg: executorDriver call sendStateUpdate()
    def statusUpdate(self, driver, update):
        # log
        logging.debug('Status update TID %s %s',
                      update.task_id.value,
                      update.state)



