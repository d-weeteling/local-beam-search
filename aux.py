from problems import *
from constants import *

import random
import bisect
import math

def getMinMaxSumAvg(ls, ROUND_AVG=True):

    #if len(ls) < 1:
    #   return (-1, -1, -1, -1)

    mmin = ls[0]
    mmax = ls[0]
    summ = 0

    for val in ls:
        if val < mmin: mmin = val
        if val > mmax: mmax = val
        summ += val

    avg_ = summ / float(max(1, len(ls)))
    avg_ = round(avg_) if ROUND_AVG else avg_

    return (mmin, mmax, summ, avg_)

def standardDeviation(ls):
    m = 0.0
    s = 0.0
    k = 1
    for val in ls:
        m2 = m
        m += (val - m2) / k
        s += (val - m2) * (val - m)
        k += 1
    return math.sqrt(s / (k - 1))

def problem2name(problem):

    if len(problem) is 4:
        if problem[0] == SMALL[0]:
            return "4x4 'SMALL' (extra)"

    if len(problem) is 9:
        if problem[0] == PROBLEM0[0]:
            return "9x9 'PROBLEM0' (hard)"
        if problem[0] == PROBLEM1[0]:
            return "9x9 'PROBLEM1' (harder)"
        if problem[0] == PROBLEM2[0]:
            return "9x9 'PROBLEM2' (hardest)"
        if problem[0] == PROBLEM3[0]:
            return "9x9 'PROBLEM3' (extra)"

    if len(problem) is 16:
        if problem[0] == PROBLEM16_0[0]:
            return "16x16 'PROBLEM16_0' (extra)"
        if problem[0] == PROBLEM16_1[0]:
            return "16x16 'PROBLEM16_1' (hard)"
        if problem[0] == PROBLEM16_2[0]:
            return "16x16 'PROBLEM16_2' (harder)"
        if problem[0] == PROBLEM16_3[0]:
            return "16x16 'PROBLEM16_3' (hardest)"

    return "unknown"

def getEmptyGrid():
    return [[None for _ in RNGa] for _ in RNGa]

def elementsInCommon(ls1, ls2):
    return sum([1 for el in ls1 if el in ls2])
'''
def fieldgrid2nrgrid(fgrid):
    return [[fgrid[y][x].value for x in RNGa] for y in RNGa]
'''
def countDoubles(ls):
    return sum([1 for (i, elem) in enumerate(ls) if elem in ls[i+1:]])

def nrgrid2score(nrgrid):

    rows = [[] for _ in RNGa]
    cols = [[] for _ in RNGa]

    for y in RNGa:
        rows[y] = nrgrid[y]
        for x in RNGa:
            cols[x].append(nrgrid[y][x])

    return sum([countDoubles(row) for row in rows]) + sum([countDoubles(col) for col in cols])

def coords2blocknr(x, y):
    return (y // LEN1) * LEN1 + (x // LEN1)

def mychoice(iterable, length):
    # This functions works like random.choice(), except that it also
    # works for generators (but only for finite/known length generators)
    # This is about twice as fast as first converting the generator to a list,
    # and then using random.choice() on the list.
    #print("mychoice()")
    #print("ok so far... iterable =", iterable)
    index = 0
    for item in iterable:
        restsize = length - index
        if random.random() < (1.0 / float(restsize)):
            return item
        index += 1

def myint(n):
    if n is None:
        return 0
    return n

def reprNrGrid(nrgrid):

    SYMS = set(RNGb)
    COLS = [[nrgrid[y][x] for y in RNGa] for x in RNGa]
    COL_DIFFS = [len(SYMS.difference(set(COLS[x]))) for x in RNGa]
    ROW_DIFFS = [len(SYMS.difference(set(nrgrid[y]))) for y in RNGa]
    SCORE = sum(COL_DIFFS + ROW_DIFFS)

    top_row = "|   "  + ("|" + (" %2i" * LEN1) + " ") * LEN1  +  "|"
    hori_delim = "+---"  + ("+-" + ("---" * LEN1)) * LEN1  +  "+----+\n"

    s = hori_delim[:]
    s += (top_row % tuple(RNGa)) + '    |\n'
    for y in RNGa:
        if y % LEN1 == 0:
            s += hori_delim

        s += "|%2i |" % y
        for x in RNGa:
            s += "%s" % ('  -' if nrgrid[y][x] is None else " %2i" % nrgrid[y][x])
            if (x + 1) % LEN1 == 0:
                s += " |"

        s += " %2i |\n" % ROW_DIFFS[y]
    s += hori_delim
    s += (top_row % tuple(COL_DIFFS)) + ' %i\n' % SCORE
    s += hori_delim
    return s

def printNrGrid(nrgrid):
    print(reprNrGrid(nrgrid))

if __name__ == '__main__':

    import sys
    print "module:", sys.argv[0]
    print "This module should be imported! Aborting.\n"
