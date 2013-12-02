#!/usr/bin/env python

from collections import defaultdict
htp = defaultdict(lambda: defaultdict(lambda: 0.001))

for line in open('final.dict.txt','r'):
	token = line.strip().split()
	htp[token[0]][token[2]] = float(token[1])

for line in open('inputHanzi.txt', 'r'):
	token = line.strip().split()
	py = []
	for hz in token:
		if hz not in htp:
			x=''
			for i in range(len(hz)/3):
				pt = hz[i*3:i*3+3]
				y=max(htp[pt], key=htp[pt].get)
				x+=y
		else:
			x = max(htp[hz], key=htp[hz].get)
		py.append(x)
	print ' '.join(py)



