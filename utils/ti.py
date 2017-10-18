import math
from functools import reduce
import timeit
from random import random
import sys

import numpy

arrays = [
            [random() for x in range(40000)] for x in range(100)
         ]

npaa = numpy.array(arrays)


def fn2():
    return numpy.sum(npaa, axis=0)

    
npaa2 = [numpy.array(x).reshape((200, 200)) for x in arrays]


def fn3():
    return reduce(numpy.add, npaa2)


def recalc():
    npamove = numpy.empty((200, 200))
    it = numpy.nditer(npamove, flags=['multi_index'], op_flags=['readwrite'])
    while not it.finished:
        i, j = it.multi_index
        if i == 0 and j == 0:
            den2 = float('inf')
            den = float('inf')
        else:
            den2 = (i**2 + j**2)
            den = math.sqrt(den2)
        it[0][...] = 1000/den2 - 1000/64/den
        it.iternext()


def pycalc():
    arr = numpy.empty((200, 200))
    for i in range(200):
        for j in range(200):
            if i == 0 and j == 0:
                den2 = float('inf')
                den = float('inf')
            else:
                den2 = (i**2 + j**2)
                den = math.sqrt(den2)
            arr[i, j] = 1000/den2 - 1000/64/den


if __name__ == '__main__':
    N = int(sys.argv[1])
    print("fn3", timeit.timeit(stmt=fn3, number=N))
    print("fn2", timeit.timeit(stmt=fn2, number=N))
    print("pycalc", timeit.timeit(stmt=pycalc, number=N))
    print("recalc", timeit.timeit(stmt=recalc, number=N))
