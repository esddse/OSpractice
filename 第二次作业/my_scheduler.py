
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
TASK_NUM = 10

EXECUTOR_CPUS = 0.5
EXECUTOR_MEM = 192

DATA_PATH = './anna_karenina.txt'

# read data
def readData():
    datas = [0]*TASK_NUM
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = []
        for line in f:
            line = re.sub(r'[^0-9a-zA-Z]', ' ', line.strip()) 
            line = re.sub(r'\s+', ' ', line)
            data += line.split(' ')
        data_length = len(data)
        task_length = int(data_length / TASK_NUM)

        # devide into TASK_NUM parts
        for i in range(TASK_NUM):
            datas[i] = data[ i*task_length : min((i+1)*task_length, data_length-1)]
        return datas

class MyScheduler(Scheduler):

    def __init__(self, executor):
        # executor
        self.executor = executor
        # some flags
        self.task_launched = 0
        self.task_finished = 0
        self.msg_received = 0
        # data
        self.datas = readData()
        self.word_count = {}

    # print out the counted words
    def printWordCount(self):
        for word, num in self.word_count.items():
            print(word, ' ', num)

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
            task.name = 'task {}'.format(task_id)
            task.executor = self.executor
            #task.data = encode_data(bytes('Hello from task {}!'.format(task_id), 'utf-8'))
            task.data = encode_data(bytes('ThisIsASeparator'.join(self.datas[self.task_launched]), 'utf-8'))

            task.resources = [
                dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
            ]

            # launch task
            driver.launchTasks(offer.id, [task], filters)

            self.task_launched += 1

    # receive task result
    def frameworkMessage(self, driver, executorId, slaveId, message):
        # merge task result
        result = decode_data(message).decode().split('ThisIsAnOuterSeparator')
        for item in result:
            item = item.split('ThisIsAnInnerSeparator')
            if item[0] in self.word_count:
                self.word_count[item[0]] += int(item[1])
            else:
                self.word_count[item[0]] = int(item[1])

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

        # check if task finished
        if update.state == 'TASK_FINISHED':
            self.task_finished += 1
            # check if all tasks are finished
            if self.task_finished == TASK_NUM:
                self.printWordCount()
                print('all tasks are finished, exit!')
                exit(0)



