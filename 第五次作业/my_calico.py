import sys
import logging

from addict import Dict
from my_scheduler import *



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