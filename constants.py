import itertools

LEN1    = 4                  # 3
LEN2    = LEN1 * LEN1        # 9 
RNGa    = range(LEN2)        # 0 to 8 inclusive
RNGb    = range(1, 1 + LEN2) # 1 to 9 inclusive
MAGIC   = sum(RNGb)
MAX_INT = pow(2, 32)


if __name__ == '__main__':
    
    import sys
    print "module:", sys.argv[0]
    print "This module should be imported! Aborting.\n"
    exit()

