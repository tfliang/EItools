'''
要做的事情，给每个单位一个可匹配列表
具体来说，除了原始名字，给每个单位扩展：
1. 高校缩写
2. 去掉“省”这个字以后的单位名称
'''
import os
from EItools.config.globalvar import CLASSIFIER_DIR
import sys
import re

class Aff2Pat:
	abbr = {}
	def init():
		pat = re.compile(r'“([^"]+)”')
		with open(CLASSIFIER_DIR+'/data/abbr.txt', 'r', encoding = 'utf-8') as f:
			for line in f:
				full = line.split('：')[0]
				Aff2Pat.abbr[full] = []
				for x in pat.findall(line):
					Aff2Pat.abbr[full].append(x)
	
	def get_pat(aff):
		res = [aff]
		L = len(aff)
		for i in range(L, 0, -1):
			if aff[:i] in Aff2Pat.abbr:
				for x in Aff2Pat.abbr[aff[:i]]:
					res.append(x+aff[i:])
				break
		qd = []
		for x in res:
			if x.find('省') != -1:
				qd.append(x.replace('省', ''))
		return '|'.join(res + qd)
	