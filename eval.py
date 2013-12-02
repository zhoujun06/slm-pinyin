#!/usr/bin/env python

import sys
import itertools

try:
    _, testfilename, goldfilename = sys.argv
except:
    sys.stderr.write("usage: evalb.py <test-file> <gold-file>\n")
    sys.exit(1)

m = n = 0
for testline, goldline in itertools.izip(open(testfilename), open(goldfilename)):
    n += len( goldline.strip().split())
    for testtok, goldtok in itertools.izip(testline.strip().split(), goldline.strip().split()):
        if testtok == goldtok:
            m += 1

print "total words:  ", n
print "correct words: ", m
print "accuracy:     ", float(m)/n
