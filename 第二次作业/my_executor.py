
import logging
import sys
import time
import json
from threading import Thread

from pymesos import MesosExecutorDriver, Executor, encode_data, decode_data
from addict import Dict


class MyExecutor(Executor):

    def launchTask(self, driver, task):
        def run_task(task):
            # config start state
            update = Dict()
            update.task_id.value = task.task_id.value
            update.state = 'TASK_RUNNING'
            update.timestamp = time.time()
            driver.sendStatusUpdate(update)


            # word count
            # ----------------------------------------
            # data preparation
            words = decode_data(task.data).decode().split('ThisIsASeparator')
            
            # count words 
            word_count = {}
            for word in words:
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

            # prepare result
            result = []
            for word, cnt in word_count.items():
                result.append(word+'ThisIsAnInnerSeparator'+str(cnt))           
            result = 'ThisIsAnOuterSeparator'.join(result)       

            # send result to scheduler
            driver.sendFrameworkMessage(encode_data(bytes(result, 'utf-8')))
            # ----------------------------------------
            
            # config end state
            update = Dict()
            update.task_id.value = task.task_id.value
            update.state = 'TASK_FINISHED'
            update.timestamp = time.time()
            driver.sendStatusUpdate(update)

        # run agent thread
        thread = Thread(target=run_task, args=(task,))
        thread.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    driver = MesosExecutorDriver(MyExecutor(), use_addict=True)
    driver.run()
