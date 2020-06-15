#
# run command: locust --host=localhost:9000
#

import inspect
import time

from locust import Locust, TaskSet, task, events

import cStringIO
import os
import sys
import time
import ccnlite.client
import ccnlite.ndn2013 as ndn


def printIt(pkts):
    if pkts != None and pkts[0] != None:
        name, content = ndn.parseData(cStringIO.StringIO(pkts[0]))
        print (content)


def stopwatch(func):
    def wrapper(*args, **kwargs):
        # get task's function name
        previous_frame = inspect.currentframe().f_back
        _, _, task_name, _, _ = inspect.getframeinfo(previous_frame)

        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(request_type="TYPE",
                                        name=task_name,
                                        response_time=total,
                                        exception=e)
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(request_type="TYPE",
                                        name=task_name,
                                        response_time=total,
                                        response_length=0)
        return result

    return wrapper


class CCNClient:
    def __init__(self, host):
        host = host.split(':')
        self.host = str(host[0])
        self.port = int(host[1])

    def new_connection(self):
        # do some magic to establish connection
        print("new connection to " + self.host + ":" + str(self.port))
        nw = ccnlite.client.Access()
        nw.connect(self.host, self.port)
        return None

    @stopwatch
    # this is the method we want to measure
    def upload_set(self, set):
        # do some magic to upload data set
        print("uploading set: " + set)
        #time.sleep(2.4)
        nw = ccnlite.client.Access()
        nw.connect(self.host, self.port)
        printIt(nw.getLabeledResult("/pynfn/hello", set))
        return True

    def close_connection(self):
        # do some magic to close connection
        print("connection closed")
        time.sleep(1)
        return None


class CCNLocust(Locust):
    def __init__(self):
        super(CCNLocust, self).__init__()
        self.client = CCNClient(self.host)

        
class CCNTasks(TaskSet):
    @task(1)
    def task_dpi6(self):
        #self.client.new_connection()
        self.client.upload_set("call 2 /myNamedFunctions/getDPI6 /test/data")
        #self.client.close_connection()

    @task(2)
    def task_hello(self):
        #self.client.new_connection()
        self.client.upload_set("call 1 /myNamedFunctions/returnHelloWorld")
        #self.client.close_connection()        


class CCNUser(CCNLocust):
    task_set = CCNTasks
    min_wait = 100
    max_wait = 200
