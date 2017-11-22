# -*- coding: utf-8 -*-
"""
Created on Nov 22 10:40 2017
@author(s): Aaron Chall
taken from:
https://stackoverflow.com/questions/492519/timeout-on-a-function-call

Creates a decorator which is able to kill processes if they take too long.
"""
import sys
import threading
from time import sleep

try:
    import thread
except ImportError:
    import _thread as thread


def cdquit(fn_name):
    # print to stderr, unbuffered in Python 2.
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush()  # Python 3 stderr is likely buffered.
    thread.interrupt_main()  # raises KeyboardInterrupt


def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''

    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, cdquit, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result

        return inner

    return outer


@exit_after(1)
def a():
    print('a')


@exit_after(2)
def b():
    print('b')
    sleep(1)


@exit_after(3)
def c():
    print('c')
    sleep(2)


@exit_after(4)
def d():
    print('d started')
    for i in range(10):
        sleep(1)
        print(i)


@exit_after(5)
def countdown(n):
    print('countdown started', flush=True)
    for i in range(n, -1, -1):
        print(i, end=', ', flush=True)
        sleep(1)
    print('countdown finished')


def main():
    a()
    b()
    c()
    try:
        d()
    except KeyboardInterrupt as error:
        print('d should not have finished, printing error as expected:')
        print(error)
    countdown(3)
    countdown(10)
    print('This should not print!!!')


if __name__ == '__main__':
    main()
