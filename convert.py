#!/usr/bin/env python

#junzhou@usc

import sys, re, logging
import math
from collections import defaultdict
from bigfloat import bigfloat,log10

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)
logger = logging.getLogger(__name__)

alphabet = 'abcdefghijklmnopqrstuvwxyz'

class PyToChar():
	"""
	given pinyin sequence separated by space
	output Chinese character sequence separated by space
	using p(ch) and bigram model
	"""
	def __init__(self):
		self._dict = defaultdict(lambda: defaultdict(lambda: 0.001))
		self._lm = defaultdict(lambda: defaultdict(lambda: 0.001))
		self._pyfreq = defaultdict(lambda: 0.001)
		self._typo = {}
		self._typo_p = None

	def loadDict(self, fdict):
		"""
		load pinyin to char dictionary
		ba1 3193.1902591 ba
		ba2 3625.99770514 ba
		need to normalize freq
		"""
		total = 0
		for line in open(fdict, 'r'):
			token = line.strip().split()
			freq = float(token[1])
			self._dict[token[2]][token[0]] =  freq
			total += freq

		#normalize
		for py in self._dict:
			for ch in self._dict[py]:
				self._dict[py][ch] /= total

	def loadLM(self, flm):
		"""
		load language model, bigram
		*S* dan1 0.010070895776 *S* dan
		"""
		for line in open(flm, 'r'):
			token = line.strip().split()
			ch1 = token[0]
			ch2 = token[1]
			freq = bigfloat(float(token[2]))
			self._lm[ch1][ch2] += freq

	def loadPyFreq(self, fpy):
		for line in open(fpy,'r'):
			token = line.strip().split()
			py = token[0]
			freq = math.log(float(token[1]))
			self._pyfreq[py] = freq

	def loadTypo(self, fty):
		typo1 = {}
		typo2 = {}
		for line in open(fty,'r'):
			token = line.strip().split()
			typo1[token[0]] = token[1]
			typo2[token[1]] = token[0]
		ty = '('+'|'.join(typo1.keys()) + '|' + '|'.join(typo2.keys()) + ')'
		self._typo.update(typo1)
		self._typo.update(typo2)
		self._typo_p = re.compile(ty)
		#print ty


	def correct(self, seq):
		"""
		when seq is not in self._dict, try possible correction
		"""
		#1. common typos
		seq_org = seq
		pys = []
		p1 = ''
		#print seq
		while True:
			res = self._typo_p.search(seq)
			if not res:
				break
			ch1 = res.group(1)
			ch2 = self._typo[ch1]
			start = res.start()
			end = res.end()
			new = p1+seq[0:start]+ch2+seq[end:]

			p1 += seq[0:end]
			seq = seq[end:]
			#print ch1, ch2, start, end
			#print p1, seq
			#print new

			if new in self._pyfreq:
				pys.append(new)

		#print pys
		if len(pys) > 0 :
			return max(pys, key=self._pyfreq.get)
		else:
			return self.correctED(seq_org)
	
	# the following four methods of edit distance are from http://norvig.com/spell-correct.html
	def edits1(self, word):
		splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		deletes    = [a + b[1:] for a, b in splits if b]
		transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
		replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
		inserts    = [a + c + b     for a, b in splits for c in alphabet]
		return set(deletes + transposes + replaces + inserts)

	def known_edits2(self, word):
		return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self._pyfreq)

	def known(self, words): return set(w for w in words if w in self._pyfreq)

	def correctED(self, word):
		candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word)
		return max(candidates, key=self._pyfreq.get) if len(candidates) > 0 else ''

	def splitPinyinDyFreq(self, seq):
		n = len(seq)
		q = [[0.0 for i in range(n+1)] for j in range(n+1)]
		best = [[[] for i in range(n+1)] for j in range(n+1)]

		for i in range(0, n):
			py = seq[i:i+1]
			q[i][i+1] = self._pyfreq[py]
			best[i][i+1] = (i,i+1)
		
		for l in range(2,n+1):
			for i in range(0, n+1-l):
				j = i+l
				for k in range(i+1, j):
					tmp = q[i][k] + q[k][j]
					if tmp > q[i][j]:
						q[i][j] = tmp
						best[i][j] = (i,k,j)
				if seq[i:j] in self._pyfreq:
					q[i][j] += self._pyfreq[seq[i:j]]
					best[i][j] = (i,j)

		py = self.extract(seq, best, 0, n)
		return py

	def extract(self, seq, best, i, j):
		if len(best[i][j]) == 0:
			return ''
		if len(best[i][j]) == 2:
			return seq[i:j]
		else:
			i,k,j = best[i][j]
			return self.extract(seq, best, i, k) + ' ' + self.extract(seq, best, k, j)


	def getCharsFromPinyin(self, seq):
		chs = []
		token = seq.strip().split()
		for i,py in enumerate(token):
			if py in self._dict:
				chs.append(self._dict[py].keys())
			else:
				#print 'err ' + py
				tp = self.correct(py)
				#print 'correct: ' + tp
				if tp in self._dict:
					token[i] = tp
					chs.append(self._dict[tp].keys())
					self._dict[py] = self._dict[tp]
				else:
					if len(py) > 2:
						pysp = self.splitPinyinDyFreq(py)
						if pysp == '':
							a=1
							self._dict[py]['NUL'] = 0.001
						else:
							#print 'split: ' + pysp
							ch = self.convert(pysp).replace(' ', '')
							self._dict[py][ch] = 0.001
					else:
						a=1
						self._dict[py]['NUL'] = 0.001
					self._pyfreq[py] = 1.0
					chs.append(self._dict[py].keys())
		return (token, chs)


	def convert(self, seq):
		"""
		given pinyin sequence, convert
		"""
		token, chs = self.getCharsFromPinyin(seq)
		#print seq

#		print 'chs'
#		for x in chs:
#			for y in x:
#				print y
#		print 'end chs'
		q = [[0.0 for i in range(len(x))] for x in chs]
		best = [[0 for i in range(len(x))] for x in chs]
		
		for j in range(len(q[0])):
			py = token[0]
			ch = chs[0][j]
			#q[0][j] = self._dict[py][ch] * self._lm['*S*'][ch]
			q[0][j] = self._dict[py][ch]

		for i in range(1, len(token)):
			for j in range(len(q[i])):
				for k in range(len(q[i-1])):
					py = token[i]
					ch = chs[i][j]
					ch1 = chs[i-1][k]
					tmp = self._dict[py][ch] * self._lm[ch1][ch] * q[i-1][k]
					if tmp > q[i][j]:
						q[i][j] = tmp
						best[i][j] = k

		final_best = 0
		final_idx = 0
		i = len(token)-1
		for j in range(len(q[i])):
			if q[i][j] > final_best:
				final_best = q[i][j]
				final_idx = j

		chs_out = []
		chs_out.append(chs[i][final_idx])
		
		pre = best[i][final_idx]
		for i in range(len(token)-2, -1, -1):
			chs_out.append(chs[i][pre])
			pre = best[i][pre]

		return ' '.join(chs_out[::-1])


ptc = PyToChar()
ptc.loadTypo('final.typo.txt')
ptc.loadDict('final.dict.txt')
ptc.loadLM('final.lm.txt')
ptc.loadPyFreq('final.pyfreq.txt')

@app.route('/convert', methods=['POST', 'GET'])
def convert():
	py = request.args.get('pinyin')

	logger.debug(py)
	out = ptc.convert(py)
	return make_response(out, 200)



if __name__ == '__main__':
	app.run(debug = True)
#	print ptc.convert('xiao li chongbu peidai xiaohui l')
	#print ptc.convert('xurongxin shi ta buneng anyu daxue li de qingping shenghuo')
	#for line in open('inputPinyinok.txt','r'):
	#	print ptc.convert(line)
	#	print ptc.convert(line.replace(' ', ''))
#	while True:
#		line = sys.stdin.readline()
#		print ptc.convert(line)



