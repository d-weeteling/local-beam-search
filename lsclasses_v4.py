from problems import *
from constants import *
from randomgrid import buildGrid

import random
import bisect
import math
import copy
import aux

DBG = False

class Field:
    
    def __init__(self, x, y, initvalue, fixed):
        self.coords = (x, y)
        self.value = initvalue if initvalue else 0
        self.fixed = fixed

    def __repr__(self):
        s = "(%i, %i):" % self.coords
        s += ("[%i]" % self.value) if self.fixed else ("%i" % self.value)
        return s
   
        
class Block:
    
    def __init__(self, fieldRow):
        
        def getSwappablePairs():
            result = []
            for i in range(len(self.core)):
                if not self.core[i].fixed:
                    for j in range(i + 1, len(self.core)):
                        if not self.core[j].fixed:    
                            result.append((self.core[i], self.core[j]))
            return tuple(result)
        
        self.core = fieldRow
        self.swappable = getSwappablePairs()

    def __repr__(self):
        s = ""
        for (i, el) in enumerate(self.core):
            s += str(el).ljust(12)
            if ((i + 1) % LEN1) is 0:
                s += '\n'
        return s
       
       
class Zone:      
    
    def mutate(self, index1, partnerzone, index2, newval):
        # Replaces a value in a field, and does related bookkeeping.
        
        if DBG: assert self.core[index1] is partnerzone.core[index2]
        
        oldval = self.core[index1].value
        deltascore = 0
        
        if oldval in self.redundantvalues:
            self.redundantvalues.remove(oldval)
            self.score -= 1
            deltascore -= 1
            
        if oldval in partnerzone.redundantvalues:
            partnerzone.redundantvalues.remove(oldval)
            partnerzone.score -= 1
            deltascore -= 1

        if newval in [fld.value for fld in self.core]:
            self.redundantvalues.append(newval)
            self.score += 1
            deltascore += 1

        if newval in [fld.value for fld in partnerzone.core]:
            partnerzone.redundantvalues.append(newval)
            partnerzone.score += 1
            deltascore += 1

        self.core[index1].value = newval
        partnerzone.core[index2].value = newval
        return deltascore
            
    def updateRedundantValues(self):
        self.redundantvalues = self.__getRedundantValues()       
        
    def __getRedundantValues(self):
        fieldRow = self.core
        nrRow = [field.value for field in fieldRow]
        result = []
        self.score = 0
        for (i, fld) in enumerate(fieldRow):
            if fld.value in nrRow[i+1:]:
                self.score += 1
                result.append(fld.value)
        return result
          
    def __init__(self, fieldrow):
        self.core = fieldrow
        self.score = MAX_INT
        self.updateRedundantValues()
     
    def __repr__(self):
        return str(self.core)
        
    def printData(self):
        print("self.core..............:", self.core)
        print("self.score.............:", self.score)
        print("self.redundantvalues...:", self.redundantvalues)
        print()
  

class LimitedMinList:
    """class LimitedMinList
    
    This datastructure is list with a fixed-size maximum length. The list is kept
    in ascending order. It has a __iter__ method to retrieve it's content, and a
    dedicated getcore() method to get the list. Uses the bisect library.
    
    To be used for e.g. keeping track of the "n best successors". """
    
    def getcore(self):
        return self.__core

    def append(self, obj):
        bisect.insort_left(self.__core, obj) 
        if self.__cursize == self.__maxsize:
            self.__core.pop()
        else:
            self.__cursize += 1
                
    def __init__(self, MAX_SIZE=MAX_INT):
        self.__core = []
        self.__cursize = 0
        self.__maxsize = MAX_SIZE
        
    def __repr__(self):
        return str(self.__core)
        
    def __iter__(self):
        return iter(self.__core)
        
    def __contains__(self, obj):
        return obj in self.__core
    
    def __len__(self):
        return self.__cursize
    
    
class LocalSearch:
    
    def getBestMoves(self, n, RETURN_SCORE=True):
          
        oldscore = self.score
        result = LimitedMinList(MAX_SIZE=n)

        for (fld1, fld2) in self.SWAPPABLE_PAIRS:
              
            if DBG:
                assert len(result) <= n
                assert self.score == oldscore == self.getScore()

            # phase I - prep;
            (val1, x1, y1, oldsum_x1, oldsum_y1) = self.__prepMutation(fld1)
            (val2, x2, y2, oldsum_x2, oldsum_y2) = self.__prepMutation(fld2)
            
            # phase II - mutation;
            deltascore = self.makeMove(oldscore, x1, y1, x2, y2, UPDATE_SCORE=True, UPDATE_LOSCORE=False)
            #newscore = oldscore + deltascore #self.getScore()

            # phase III - undo mutation;
            self.__undoMutation(oldscore, val1, x1, y1, oldsum_x1, oldsum_y1, val2, x2, y2, oldsum_x2, oldsum_y2)
            
            #self.score = oldscore #self.getScore()
            result.append((deltascore, x1, y1, x2, y2) if RETURN_SCORE else (x1, y1, x2, y2))
            
            if DBG: assert oldscore is self.score

        return result.getcore()
    
    
    def makeFirstBestMove(self):
        
        oldscore = self.score
        
        for (fld1, fld2) in self.SWAPPABLE_PAIRS:

            if DBG:
                assert self.score == oldscore
                assert self.score == aux.nrgrid2score(self.getNrGrid())
                assert self.score == self.getScore()
            
            (val1, x1, y1, oldsum_x1, oldsum_y1) = self.__prepMutation(fld1)
            (val2, x2, y2, oldsum_x2, oldsum_y2) = self.__prepMutation(fld2)

            deltascore = self.makeMove(oldscore, x1, y1, x2, y2, UPDATE_SCORE=True, UPDATE_LOSCORE=False)
            if deltascore < 0:
                return True
            else:
                self.__undoMutation(oldscore, val1, x1, y1, oldsum_x1, oldsum_y1, val2, x2, y2, oldsum_x2, oldsum_y2)
                    
        return False
    
    
    def makeTrueBestMove(self, ONLY_POSMOVES=True):
        
        oldscore = self.score
        bestmove = (99, None, None, None, None)
        found_potential_best = False
    
        for (fld1, fld2) in self.SWAPPABLE_PAIRS:

            if DBG:
                assert self.score == oldscore
                assert self.score == aux.nrgrid2score(self.getNrGrid())
                assert self.score == self.getScore()
            
            (val1, x1, y1, oldsum_x1, oldsum_y1) = self.__prepMutation(fld1)
            (val2, x2, y2, oldsum_x2, oldsum_y2) = self.__prepMutation(fld2)
            
            deltascore = self.makeMove(oldscore, x1, y1, x2, y2)
            if deltascore is -4:
                return True
            else:
                self.__undoMutation(oldscore, val1, x1, y1, oldsum_x1, oldsum_y1, val2, x2, y2, oldsum_x2, oldsum_y2)
                if ((ONLY_POSMOVES and deltascore < 0 and deltascore < bestmove[0])
                     or
                    (not ONLY_POSMOVES and deltascore < bestmove[0])):
                    
                        found_potential_best = True
                        bestmove = (deltascore, x1, y1, x2, y2)
            
        if found_potential_best:
            self.makeMove(oldscore, *bestmove[1:])
            return True
        else:
            return False


    def makeMove(self, oldscore, x1, y1, x2, y2, UPDATE_SCORE=True, UPDATE_LOSCORE=True):
        
        val1 = self.fieldgrid[y1][x1].value
        val2 = self.fieldgrid[y2][x2].value
        
        # The actual swapping of the two cells' values
        deltascore_pt1 = self.rows[y1].mutate(x1, self.cols[x1], y1, val2)
        deltascore_pt2 = self.rows[y2].mutate(x2, self.cols[x2], y2, val1)
        
        #self.fieldgrid[y1][x1].value = val2
        #self.fieldgrid[y2][x2].value = val1

        # We adjust the score for the affected row(s) and column(s)
        
        '''
        self.row_scores[y1] = self.rows[y1].score
        self.row_scores[y2] = self.rows[y2].score
        self.col_scores[x1] = self.cols[x1].score
        self.col_scores[x2] = self.cols[x2].score
        '''
        
        if UPDATE_SCORE:
            self.score = oldscore + (deltascore_pt1 + deltascore_pt2) #self.getScore()
            
        if UPDATE_LOSCORE:
            self.__updateLoScore()
            
        return deltascore_pt1 + deltascore_pt2
            

    def getScore(self):
        return sum(self.row_scores) + sum(self.col_scores)
    
    
    def getNrGrid(self):
        return [[self.fieldgrid[y][x].value for x in RNGa] for y in RNGa]
    
    
    def __updateContinued(self, RESET_INITSCORE, RESET_LOSCORE):
        
        for i in RNGa:
            self.rows[i].updateRedundantValues()
            self.cols[i].updateRedundantValues()
            
        self.row_scores = [row.score for row in self.rows]
        self.col_scores = [col.score for col in self.cols]
    
        self.score = self.getScore()
        
        if RESET_INITSCORE:
            self.NRGRID_INITSCORE = self.score
        
        if RESET_LOSCORE:
            self.lo_score = self.score
        
    
    def updateFromNrGrid(self, nrgrid, RESET_INITSCORE=True, RESET_LOSCORE=True):
        
        for y in RNGa:
            for x in RNGa:
                self.fieldgrid[y][x].value = nrgrid[y][x]  
        self.__updateContinued(RESET_INITSCORE, RESET_LOSCORE)
        

    def updateFromHasj(self, hasj, RESET_INITSCORE=True, RESET_LOSCORE=True):
        
        hasjlist = filter(lambda s:s, hasj.split('i'))
        for y in RNGa:
            for x in RNGa:
                self.fieldgrid[y][x].value = int(hasjlist[x + y * LEN2])
        self.__updateContinued(RESET_INITSCORE, RESET_LOSCORE)
       
       
    def __updateLoScore(self):
        
        if self.score < self.lo_score:
            self.lo_score = self.score
    
    
    def __prepMutation(self, fld):
        
        (x, y) = fld.coords
        return (fld.value, x, y, self.col_scores[x], self.row_scores[y])
        
        
    def __undoMutation(self, oldscore, val1, x1, y1, oldsum_x1, oldsum_y1, val2, x2, y2, oldsum_x2, oldsum_y2):
        
        self.rows[y1].mutate(x1, self.cols[x1], y1, val1)
        self.rows[y2].mutate(x2, self.cols[x2], y2, val2)

        self.row_scores[y1] = oldsum_y1
        self.row_scores[y2] = oldsum_y2
        self.col_scores[x1] = oldsum_x1
        self.col_scores[x2] = oldsum_x2
        
        self.score = oldscore
                        
                                             
    def __init__(self, problem, RANDOMIZE=True):
        
        def __buildFieldGrid():
            
            fieldgrid = aux.getEmptyGrid()
            
            rows   = [[] for _ in RNGa]
            cols   = [[] for _ in RNGa]
            blocks = [[] for _ in RNGa]
            
            for y in RNGa:
                for x in RNGa:
                    fieldgrid[y][x] = Field(x, y, self.NRGRID_INIT[y][x], bool(self.NRGRID_PROBLEM[y][x]))
                    cols[x].append(fieldgrid[y][x])
                    blocks[aux.coords2blocknr(x, y)].append(fieldgrid[y][x])
                rows[y] = fieldgrid[y]
                
            self.rows   = [Zone(fldrow)  for fldrow in rows];       del(rows)
            self.cols   = [Zone(fldcol)  for fldcol in cols];       del(cols)
            self.blocks = [Block(fldblk) for fldblk in blocks];     del(blocks)
            
            return fieldgrid
             
        if DBG: assert LEN2 == len(problem) == len(problem[0])
            
        self.NRGRID_PROBLEM     = problem
        self.NRGRID_INIT        = buildGrid(problem, RANDOM_ORDER=RANDOMIZE)
        self.PROBLEM_NAME       = aux.problem2name(problem)
        self.fieldgrid          = __buildFieldGrid()
        self.SWAPPABLE_PAIRS    = tuple([x for tup in [b.swappable for b in self.blocks] for x in tup])
        self.SWAPPABLE_SIZE     = len(self.SWAPPABLE_PAIRS)
        self.iterations         = 0
        self.row_scores         = [row.score for row in self.rows]
        self.col_scores         = [col.score for col in self.cols]
       
        self.score = self.lo_score = self.NRGRID_INITSCORE = self.getScore()


    def __repr__(self):
        return aux.reprNrGrid(self.getNrGrid())
    
    
    def printData(self, NL=True):
        
        print "[S] sudoku............:", self.PROBLEM_NAME
        print "[S] debug mode........:", DBG
        print "[S] iterations........:", self.iterations
        print "[S] possible swaps....:", self.SWAPPABLE_SIZE
        #print "[S] init score........:", "I" * self.NRGRID_INITSCORE, str(self.NRGRID_INITSCORE) + ")"
        print "[S] self.lo_score.....:", "#" * self.lo_score, str(self.lo_score) + ")"
        print "[S] self.score........:", "X" * self.score, str(self.score) + ")"
        if NL: print
    
    
    def hasj(self):
        nrgrid = self.getNrGrid()
        return 'i'.join([str(nrgrid[y][x]) for y in RNGa for x in RNGa])
        
 

if __name__ == '__main__':
    
    ls = LocalSearch(PROBLEM16_1)
    
    h = ls.hasj()
    print ls
    ls.printData()
    print h
    
    nrgrid1 = ls.getNrGrid()
    
    ls.updateFromNrGrid(buildGrid(ls.NRGRID_PROBLEM, RANDOM_ORDER=True))
    
    print ls
    
    ls.updateFromHasj(h)
    nrgrid2 = ls.getNrGrid()
    print ls
    ls.printData()
    assert nrgrid1 == nrgrid2
    exit()
    
    import sys
    print "module:", sys.argv[0]
    print "This module should be imported! Aborting.\n"
    exit()



