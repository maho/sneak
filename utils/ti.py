import math
from functools import reduce
import timeit
from random import random
import sys

import numpy

A = numpy.array(range(1000))
B = numpy.array(range(1000,2000))


def normal():
    for x, y in zip(A, B):
        _r = 1 / (x**2 + y**2)


def bynumpy():
    _R = (1 / (A ** 2 + B ** 2))


def sqnormal():
    for x, y in zip(A, B):
        _r = 1 / math.sqrt(x**2 + y**2)


def sqbynumpy():
    _R = numpy.sqrt(1 / (A ** 2 + B ** 2))



if __name__ == '__main__':
    N = int(sys.argv[1])
    for x in (normal, sqnormal, bynumpy, sqbynumpy):
        print(x, timeit.timeit(stmt=x, number=N))
