from cars import GetCars
from appraise import AppraiseCar

from threading import Thread
from queue import Queue

import json

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)

        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return

class Comparisons:
    def __init__(self, query):
        self.workers = Queue()
        self.query = query

    def __call__(self):
        return self.run()

    def run(self):
        slaves_thread = Thread(target=self.slaves)
        slaves_thread.start()
        return self.master()

    def master(self):
        count = 0
        while True: # not workers.empty()
            worker = self.workers.get()
            item = worker.join()
            self.workers.task_done()
            if item is not None:
                json_item = json.dumps(worker.join())
                yield json_item
            elif item is False:
                print('All done!!')
                break

    def slaves(self):
        cars = GetCars(self.query)
        for car in cars():
            car_appraisal = AppraiseCar(car)
            worker = ThreadWithReturnValue(target=car_appraisal.run)
            worker.start()
            self.workers.put(worker)

if __name__ == '__main__':
    query = {
        'region': 'sfbay',
        'make': 'honda',
        'model': 'accord'
    }
    comparisons = Comparisons(query)
    for comparison in comparisons():
        print(comparison)
