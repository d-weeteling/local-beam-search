from aux import *
from constants import *
from problems import *

import itertools
import random


def buildRow(presetrow, randomize=True):

    legalvals = set(RNGb).difference(set(presetrow))
    if randomize:
        legalvals = list(legalvals)
        random.shuffle(legalvals)

    resultrow = presetrow[:]

    for i in RNGa:
        if not presetrow[i]:
            resultrow[i] = legalvals.pop()

    return resultrow

def nrgrid2rows(nrgrid):

    def coords2blockindex(x, y):
        return (x // LEN1) + ((y // LEN1) * LEN1)

    result = [[] for _ in RNGa]
    for y in RNGa:
        for x in RNGa:
            index = coords2blockindex(x, y)
            result[index].append(nrgrid[y][x])

    return result

def rows2nrgrid(rowarr):

    def blockindex2coords(index1, index2):
        return ((index1  % LEN1) * LEN1 + (index2  % LEN1),
                (index1 // LEN1) * LEN1 + (index2 // LEN1))

    result = [[None for _ in RNGa] for _ in RNGa]
    for (i, row) in enumerate(rowarr):
        for j in RNGa:
            (x, y) = blockindex2coords(i, j)
            result[y][x] = row[j]

    return result

def buildGrid(presetgrid, RANDOM_ORDER=False):

    rs = nrgrid2rows(presetgrid)

    rsfilled = []
    for presetrow in rs:
        row = buildRow(presetrow, RANDOM_ORDER)
        rsfilled.append(row)

    return rows2nrgrid(rsfilled)


if __name__ == '__main__':

    import sys
    print("module:", sys.argv[0])
    print("This module should be imported! Aborting.\n")
    exit()
