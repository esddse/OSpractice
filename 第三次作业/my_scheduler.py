
import re
import sys
import uuid
import logging
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data, decode_data
from addict import Dict

TASK_CPU = 0.1
TASK_MEM = 96
TASK_NUM = 1

EXECUTOR_CPUS = 0.5
EXECUTOR_MEM = 192


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
            # check if the offer satisfy the requirments
            cpus = self.getResource(offer.resources, 'cpus')
            mem = self.getResource(offer.resources, 'mem')
            if cpus < TASK_CPU or mem < TASK_MEM:
                continue

            # config a new task
            task = Dict()
            task_id = str(uuid.uuid4())
            task.task_id.value = task_id
            task.agent_id.value = offer.agent_id.value
            task.name = 'nginx'
            # container
            task.container.type='DOCKER'
            task.container.docker.image = 'esddse/my_nginx'
            task.container.docker.network = 'HOST'
            # command 
            task.command.shell = False
            task.command.value = '/usr/local/nginx/sbin/nginx'
            task.command.arguments=['-g','daemon off;']


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



