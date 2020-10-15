import aux
import time
import bisect

from constants import *
from problems import *
from lsclasses_v4 import *
from randomgrid import buildGrid

K_MIN  = 2
K_MAX  = 32
K_INIT = K_MIN
K_MULT = 2
K      = K_MIN

DBG                  = False
MIXIN_OLDSTATES      = False
USE_BEST_PARENT      = False
LIMIT_ITERATIONS     = True
LIMIT_TIME           = False
SMART_START          = False
VERBOSE              = False

SMART_START_TRIES    = 1000
MAX_ITERATIONS       = 10000 if LIMIT_ITERATIONS else MAX_INT
MAX_TIME             = 500 if LIMIT_TIME else MAX_INT
MAX_MOVES_WO_IMPROVE = 50


class LocalBeamSearch(LocalSearch):
    
    def start(self, VERBOSE=True):
        
        global K
    
        def mytime(): return time.time() - start_time
        
        def cc1(): return not (L_[0][0] is 0)  
        def cc2(): return self.iterations < MAX_ITERATIONS
        def cc3(): return mytime() < MAX_TIME
        
        def printData():
            
            moves_untill_K_increase = MAX_MOVES_WO_IMPROVE - (sincelo % MAX_MOVES_WO_IMPROVE)
            moves_untill_K_increase_percentage = 100 * (float(moves_untill_K_increase + 1) / float(MAX_MOVES_WO_IMPROVE))
            
            print "[*] algorithm.............: Local Beam Search"
            print "[*] sudoku................:", aux.problem2name(self.NRGRID_PROBLEM)
            print "[*] debug mode............:", DBG
            print "[*] K initial max.size....:", K_INIT
            print "[*] K current max.size....: %i <= %i <= %i" % (K_MIN, K, K_MAX)
            print "[*] K current act.size....:", len(L_)
            print "[*] total time............: %.4fs" % mytime()
            print "[*] avg. time.............: %.4fms" % ((mytime()/ (self.iterations + 1)) * 1000)
            print "[*] iterations............:", self.iterations
            print "[*] possible swaps........:", self.SWAPPABLE_SIZE
            print "[*] initial_bestscore.....:", initial_bestscore
            print "[*] untill K increase.....: %2.2f%%" % min(100.0, moves_untill_K_increase_percentage)
            print "[*] untill K increase.....:", "o" * int((math.floor(moves_untill_K_increase_percentage)) / 5) + ")"
            print "[*] since lo_score x10....:", "0" * int(sincelo // 10), str(int(sincelo // 10)) + ")"
            print "[*] self.lo_score.........:", "#" * self.lo_score, str(self.lo_score) + ")"
            print "[*] self.score............:", "X" * self.score, str(self.score) + ")"
            print

        L  = self.__getInitLBSgrids(K_INIT)
        L_ = self.__getSuccLBSgrids(L, K)
        
        sincelo = 0
        start_time = time.time()
        initial_bestscore = L[0][0]
        
        CONDITIONS = [cc1, cc2, cc3]
        
        while all([c() for c in CONDITIONS]):

            '''De main-loop: 
            hier worden opvolgers van de huidige toestand berekend en vergeleken.
            '''

            L  = L_
            L_ = self.__getSuccLBSgrids(L, K)
            self.iterations += 1
            
            if L_ == []:
                
                if VERBOSE: print "[!] Cannot find any successors with a beam size %i!" % K
                if K is K_MAX:
                    if VERBOSE: print "[-] Since beam size %i is already max size, abort." % K
                    break
                else:
                    K = min(K_MAX, K_MULT * K)
                    if VERBOSE: print "[+] ..but we can still increase the beam size to", K
                    L_ = L
            
            else:
                
                curbestscore = self.score = L_[0][0]
                if curbestscore < self.lo_score:
                    
                    if curbestscore is 0:
                        if VERBOSE: print "[+] OK: found the solution!"
                        break
                    else:
                        sincelo = 0
                        self.lo_score = curbestscore
                            
                else:
                    sincelo += 1
                    if sincelo % MAX_MOVES_WO_IMPROVE == 0:
                        K = min(K_MAX, K_MULT * K)
            
            if VERBOSE: printData()
         
        self.updateFromNrGrid(L_[0][1])
        
        if VERBOSE:
            print '[!] final score (%.4fs / %i iterations):' % (mytime(), self.iterations), L_[0][0], '\n'
            print self
            
        return self.score is 0
    
    
    def __getSuccLBSgrids(self, oldstates, k):

        '''de private functie '__getSuccLBSgrids':

        De zgn. "successor functie", die mogelijke successors van de huidige toestand/spelsituatie 
        berekend. Om toestanden niet dubbel te laten berekenen en dit zo snel mogelijk te checken,
        wordt er van elke reeds berekende toestand een hash opgeslagen in de dictionary genaamd 
        'hasjmap'; in O(1) ("constante tijd") kan hiermee gekeken worden of een hash al eerder 
        berekend is.
        '''
        
        if DBG: assert 0 < len(oldstates) <= k
        
        result = []
        hasjmap = dict([(h, True) for (_, _, h) in oldstates])

        for (oldscore, oldgrid, oldhasj) in oldstates:

            self.updateFromNrGrid(oldgrid, RESET_INITSCORE=False, RESET_LOSCORE=False)
            
            for (deltascore, x1, y1, x2, y2) in self.getBestMoves(k, RETURN_SCORE=True):
                    
                if DBG:
                    assert self.score == oldscore
                    assert self.score == aux.nrgrid2score(self.getNrGrid())
                    assert self.score == self.getScore()

                '''
                In 3 fasen worden er successor states bekeken; na voorbereidingen in fase I volgt er
                in fase II een mutatie van de huidige state, waarbij de score, het grid met getallen
                en een hash worden opgeslagen.

                Door deze 3 fasen aanpak hoeft er niet steeds een volledige nieuwe sudoku gegenereerd 
                te worden (naive aanpak), waardoor de code veel sneller loopt.'''
            
                # phase I - prep;
                
                val1 = self.fieldgrid[y1][x1].value
                val2 = self.fieldgrid[y2][x2].value
                
                oldsum_y1 = self.row_scores[y1]
                oldsum_y2 = self.row_scores[y2]
                oldsum_x1 = self.col_scores[x1]
                oldsum_x2 = self.col_scores[x2]
                
                # phase II - mutation;
                
                self.makeMove(oldscore, x1, y1, x2, y2, UPDATE_SCORE=True, UPDATE_LOSCORE=False)
               
                newscore = self.score
                newgrid  = self.getNrGrid()
                newhasj  = self.hasj()

                # phase III - undo mutation;

                self.rows[y1].mutate(x1, self.cols[x1], y1, val1)
                self.rows[y2].mutate(x2, self.cols[x2], y2, val2)
        
                self.row_scores[y1] = oldsum_y1
                self.row_scores[y2] = oldsum_y2
                self.col_scores[x1] = oldsum_x1
                self.col_scores[x2] = oldsum_x2

                self.score = oldscore
                
                if not newhasj in hasjmap:
                    bisect.insort(result, (newscore, newgrid, newhasj))
                    hasjmap[newhasj] = True
        
        if MIXIN_OLDSTATES:
            '''Voor het eventuele hergebruiken voor oude states, om in een volgende iteratie vd 
            main-loop hier nieuwe, andere successors van te berekenen.
            '''
            for state in oldstates:
                bisect.insort_right(result, state)
                
        elif USE_BEST_PARENT:
            '''Voor het eventuele gebruik van de beste parent states, om in een volgende iteratie vd 
            main-loop hier nieuwe, andere successors van te berekenen.
            '''
            bisect.insort_right(result, oldstates[0])
        
        '''Slechts de eerste (=beste) k states worden gereturned.'''
        return result[:k]
    
    
    def __getInitLBSgrids(self, init_K):
        
        result = []
        
        if SMART_START:

            '''
            Door de SMART-START constante op True te zetten wordt de random begintoestand
            verbeterd; er worden relatief snel veel verschillende random begintoestanden gemaakt,
            waarvan de beste gebruikt zal worden voor het eigenlijke Beam Search algoritme.
            '''
            
            for i in range(K):
                nrgrid = buildGrid(self.NRGRID_PROBLEM, RANDOM_ORDER=True)
                bisect.insort_left(result, (aux.nrgrid2score(nrgrid), nrgrid, 'i'.join([str(nrgrid[y][x]) for y in RNGa for x in RNGa])))
            
            print "[*] SMART-START: getting %i best of %i random states..." % (K, SMART_START_TRIES)
            
            for i in range(SMART_START_TRIES - K):

                nrgrid = buildGrid(self.NRGRID_PROBLEM, RANDOM_ORDER=True)
                score = aux.nrgrid2score(nrgrid)
                
                if i == SMART_START_TRIES // 2:
                    print "[*] Halfway there. Best so far:", result[0][0] if len(result) > 0 else "undefined" 

                if score < result[-1][0]:
                    bisect.insort_left(result, (score, nrgrid, 'i'.join([str(nrgrid[y][x]) for y in RNGa for x in RNGa])))
                if len(result) > K:
                    result.pop()
                    
            print "[*] best scores:"
            print [tup[0] for tup in result]
            return result
        
        else:
            return [(self.score, self.getNrGrid(), self.hasj())]
    
 
    def __init__(self, problem, RANDOMIZE=True):
        
        if DBG: assert LEN2 is len(problem) is len(problem[0])  
        LocalSearch.__init__(self, problem, RANDOMIZE=RANDOMIZE)
        

if __name__ == '__main__':
    
    pr = PROBLEM16_1

    print "\n= LocalBeamSearch algorithm ="
    print "About to try to solve sudoku:\n"
    aux.printNrGrid(pr)
    x = raw_input("Hit the 'enter' to continue;")

    lbs = LocalBeamSearch(pr, RANDOMIZE=False)
    aux.printNrGrid(lbs.NRGRID_PROBLEM)
    lbs.start()
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
