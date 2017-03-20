import sys
import logging

from addict import Dict
from my_scheduler import *



def main(master):

    # config executor
    executor = Dict()
    executor.executor_id.value = 'MyExecutor'
    executor.name = executor.executor_id.value
    executor.command.value = '%s %s' % (
        sys.executable,
        abspath(join(dirname(__file__), 'my_executor.py'))
    )
    executor.resources = [
        dict(name='mem', type='SCALAR', scalar={'value': EXECUTOR_MEM}),
        dict(name='cpus', type='SCALAR', scalar={'value': EXECUTOR_CPUS}),
    ]


    # config framework
    framework = Dict()
    framework.user = getpass.getuser()
    framework.name = "MyFramework"
    framework.hostname = socket.gethostname()

    # init driver
    driver = MesosSchedulerDriver(
        MyScheduler(executor),
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