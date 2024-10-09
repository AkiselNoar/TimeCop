#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import time
from statistics import mean
from functools import wraps

class TimeJail:
    """
    This class collects execution time a single function and provides results
    """
    def __init__(self, fn):
        """ init with the wrapped function as parameter """
        try:
            self.name = fn.__qualname__
        except AttributeError:
            self.name = fn
        self.times = []

        #Appending times in timejail is the same as appending in times list
        self.append = self.times.append

    def __getattr__(self, key):
        """
        Attributs of this class :
        max : max time of the function
        min : min time of the function
        mean : mean time of the function
        nb_call : number of times the function was calles
        total_times : overall time of the function
        """
        d = dict(
                max=lambda: max(self.times),
                min=lambda: min(self.times),
                mean=lambda: mean(self.times),
                nb_call=lambda: len(self.times),
                total_time=lambda: sum(self.times),
                last=lambda: self.times[-1],
                )
        try:
            return d[key]()
        except KeyError:
            raise AttributeError(f"No such {key} in {type(self)}")
        except:
            if not self.times:
                # exception occured with no times inputed result in 0
                return 0
            else:
                raise

    def __add__(self, other):
        """ return the list of times appended with the other """
        return self.times + [other]

    def __iadd__(self, other):
        """ append other to list of time in this jail """
        self.times.append(other)
        return self

    def __repr__(self):
        return f"<{type(self).__qualname__} of {self.name}, mean : {self.mean} for {self.nb_call} times called>"

class TimeCop:
    """
    This class collect and measure time efficiency of a function

    usage as decorator:
    TCOP = TimeCop()

    @TCOP
    def my_func():
        # stuff
        pass

    print("mean execution time of my_func = " + TCOP[my_func].mean)

    usage as contextmanager:
    with TCOP.open("my_context"):
        #stuff
        pass

    print(TCOP["my_context"])

    usage as contextmanager with default name:
    with TCOP:
        #stuff
        pass

    print(TCOP["default"])
    """

    def __init__(self):
        self._times = {}
        self._cfunc = []
        self.wrapper = self  #For retro compatibility
        self.start = lambda n: self.open(n).__enter__()
        self.stop = self.close = self.__exit__

    def __getitem__(self, fn):
        """ return the TimeJail of the function """
        if not isinstance(fn, str):
            fn = fn.__qualname__
        return self._times[fn]

    def __setitem__(self, fn, time):
        """ adds time to the function TimeJail """
        n = fn
        if not isinstance(fn, str):
            n = fn.__qualname__
        if n not in self._times:
            self._times[n] = TimeJail(fn)
        self._times[n] += time

    def __iter__(self):
        return iter(self._times.values())

    def __call__(self, func):
        """ Actual wrapper that measure and collect execution time of functions """
        @wraps(func)
        def call(*args, **kwargs):
            self._cfunc.append(func)
            with self:
                return func(*args, **kwargs)
        return call

    def open(self, name):
        self._cfunc.append(name)
        return self

    def __enter__(self):
        if not self._cfunc:
            self._cfunc.append("default")
        self.orig = time()

    def __exit__(self, type=None, value=None, traceback=None):
        cfunc = self._cfunc.pop(-1)
        self[cfunc] = time() - self.orig

if __name__ == "__main__":
    # Example
    from time import sleep
    TCOP = TimeCop()

    class A:
        @TCOP
        def __init__(self):
            self.time()

        @TCOP
        def time(self):
            sleep(.5)

    a = A()
    a.time()

    @TCOP
    def my_sleep(t, factor=1/100):
        sleep(t*factor)

    with TCOP.wrapper:
        sleep(1)

    for i in range(10):
        my_sleep(i)

    with TCOP.open("my_context"):
        sleep(1)

    with TCOP.open("my_context"):
        sleep(0.5)


    for t  in TCOP:
        print(t)
