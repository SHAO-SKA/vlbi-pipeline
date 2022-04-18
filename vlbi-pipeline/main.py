#!/usr/bin/env python

import time

def current_time():
    cur_time = time.strftime('%Y%m%d.%H%M%S')
    print (time.strftime('%Y%m%d.%H%M%S'))
    return cur_time


if __name__ == '__main__':
    logfile = open('vlbi-pipeline.' + current_time() + '.log', 'a')
    current_time()

