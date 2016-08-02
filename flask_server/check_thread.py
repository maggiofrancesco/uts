# -*- coding: utf-8 -*-

import sys
from threading import Thread
from evolutionary import generation
from datetime import date, timedelta
from logbook import Logger, StreamHandler


StreamHandler(sys.stdout).push_application()
log = Logger('Control Thread - Urban Transport System')


class CheckThread(Thread):

    def __init__(self, thread_id, name, day):
        Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.day = day

    def run(self):
        log.notice("{0} will start".format(self.name))
        controller(self.day)
        log.warning("Be careful: {0} stopped".format(self.name))


def controller(day):
    while 1:
        if date.today() >= day:
            log.notice("Algorithm will be executed")
            day += timedelta(days=1)
            generation.main()
            log.notice("Algorithm execution finished")


def main():
    check_thread = CheckThread(1, "Control Thread", date.today())
    check_thread.start()


if __name__ == "__main__":
    main()
