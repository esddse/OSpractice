
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

            # config a new task
            task = Dict()
            task_id = str(uuid.uuid4())
            task.task_id.value = task_id
            task.agent_id.value = offer.agent_id.value
            task.name = ''
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



def main(master):

    # config framework
    framework = Dict()
    framework.user = getpass.getuser()
    framework.name = "my_calico"
    framework.hostname = socket.gethostname()

    # init driver
    driver = MesosSchedulerDriver(
        MyScheduler(),  # default executor
        framework,
        master,
        use_addict=True,
    )

    # set Ctrl+C handler, stop the driver
    def signal_handler(signal, frame):
        driver.stop()

    # run driver
    def run_driver_thread():
        driver.run()

    # init scheduler thread and run
    driver_thread = Thread(target=run_driver_thread, args=())
    driver_thread.start()

    # Ctrl+C => stop
    ('Scheduler running, Ctrl+C to quit.')
    signal.signal(signal.SIGINT, signal_handler)

    # keep alive
    while driver_thread.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        print("Usage: {} <mesos_master>".format(sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1])