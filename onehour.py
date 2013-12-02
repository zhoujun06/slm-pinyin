#!/usr/bin/env python

import sys
import math
try:
	_, fgram, ftest = sys.argv
except:
	sys.stderr.write("usage: onehour.py <unigram-file> <test-file>\n")
	sys.exit(1)

#dictionary
words = {}
for line in open(fgram,'r'):
	token = line.strip().split()
	if token[2] not in words:
		words[token[2]] = []
	words[token[2]].append(token[0])

#py frequency
pyfreq = {}
for line in open('py.freq.txt','r'):
	token = line.strip().split()
	py = token[0]
	freq = float(token[1])

	pyfreq[py] = math.log(freq)

def splitPinyinDyFreq(seq):
	print seq
	n = len(seq)
	q = [[0.0 for i in range(n+1)] for j in range(n+1)]
	best = [[[] for i in range(n+1)] for j in range(n+1)]

	for i in range(0, n):
		py = seq[i:i+1]
		#q[i][i+1] = pyfreq[py] if py in pyfreq else 0.0
		q[i][i+1] =  0.0
		best[i][i+1] = (i,i+1)
	
	for l in range(2,n+1):
		for i in range(0, n+1-l):
			j = i+l
			for k in range(i+1, j):
				tmp = q[i][k] + q[k][j]
				if tmp > q[i][j]:
					q[i][j] = tmp
					best[i][j] = (i,k,j)
			if seq[i:j] in words:
				q[i][j] += pyfreq[seq[i:j]]*l
				best[i][j] = (i,j)
				print seq[i:j]
				print best[i][j]
				print q[i][j]
	for x in best:
		print x
	for x in q:
		print x
	py = extract(seq, best, 0, n)
	return py


def splitPinyinDy(seq):
	#print seq
	n = len(seq)
	q = [[0.0 for i in range(n+1)] for j in range(n+1)]
	best = [[[] for i in range(n+1)] for j in range(n+1)]

	for i in range(0, n):
		q[i][i+1] = 1.0
		best[i][i+1] = (i,i+1)
	
	for l in range(2,n+1):
		for i in range(0, n+1-l):
			j = i+l
			if seq[i:j] in words:
				#print seq[i:j]
				q[i][j] = 1.0
				best[i][j] = (i,j)
			else:
				for k in range(i+1, j):
					tmp = q[i][k] * q[k][j] * 0.5
					if tmp > q[i][j]:
						#print i,k,j
						q[i][j] = tmp
						best[i][j] = (i,k,j)
#	for x in best:
#		print x
#	for x in q:
#		print x
	py = extract(seq, best, 0, n)
	return py

def splitPinyin(seq):
	out = []
	i = 0
	while True:
		for j in range(i+1, len(seq)+1):
			if seq[i:j] not in words:
				continue
			out.append(seq[i:j])
			i = j
			break
		if j >= len(seq):
			break
	return out


def extract(seq, best, i, j):
	if len(best[i][j]) == 2:
		return seq[i:j]
	else:
		i,k,j = best[i][j]
		return extract(seq, best, i, k) + ' ' + extract(seq, best, k, j)

test = 1
if test == 1:
	print splitPinyinDyFreq('yihongerqi')
	#print splitPinyinDyFreq('qiwangerzichenglong')
else:
	fout = open(ftest+'.out.f', 'w')
	for seq in open(ftest,'r'):
		py = splitPinyinDyFreq(seq.strip())
		print >> fout, py
		token = py.split()
		hanzi = []
		for tk in token:
			if tk in words:
				hanzi.append(words[tk][0])
			else:
				hanzi.append('NULL')
		print >> fout, ' '.join(hanzi)



