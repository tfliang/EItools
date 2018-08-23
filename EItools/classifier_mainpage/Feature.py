'''
基于词条里的摘要信息，统计每个词条的如下11个特征：
	标题
		被搜索的姓名出现的次数
		被搜索的单位出现的次数
		除了搜索的人以外，其他人名出现的次数
		除了搜索的单位以外，其他单位出现的次数
		匹配特征词：”简介|介绍|主页|领英|LinkedIn|百科”的次数
	摘要
		被搜索的姓名出现的次数
		被搜索的单位出现的次数
		除了搜索的人以外，其他人名出现的次数
		除了搜索的单位以外，其他单位出现的次数
		性别（男|女）出现的次数
		冒号、逗号、句号、顿号出现的次数
'''

import re
from .Aff2Pat import Aff2Pat
from .Extract import Extract

class Feature:
	Aff2Pat.init()
	Extract.init()
	cha = re.compile(r'简介|介绍|主页|领英|LinkedIn|百科')
	sex = re.compile(r'男|女')
	bd = re.compile(r'，|。|：|、')
	def get_name_aff(query, str):
		th = []
		name, aff = query.split(' ')
		name_pat = re.compile(re.compile(name))
		aff_pat = re.compile(Aff2Pat.get_pat(aff))
		th.append(len(name_pat.findall(str)))
		th.append(len(aff_pat.findall(str)))
		th.append(len(Extract.extract_name(str, name)))
		th.append(len(Extract.extract_aff(str, aff_pat)))
		return th
		
	def get_feature(query, item):
		'''
		get item feature of query
		'''
		title = item['title'].lower()
		text = item['text'].lower()
		special = ' \n\r'
		for ch in special:
			title = title.replace(ch, '')
			text = text.replace(ch, '')
		text = text.replace(':', '：').replace(',', '，').replace('.', '。')
		feature = []
		feature += Feature.get_name_aff(query, title)
		feature.append(len(Feature.cha.findall(title)))
		feature += Feature.get_name_aff(query, text)
		feature.append(len(Feature.sex.findall(text)))
		feature.append(len(Feature.bd.findall(text)))
		return feature