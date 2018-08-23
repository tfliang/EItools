'''
给定"姓名,单位"，返回要去搜索引擎查询的字符串

具体来说，要做的事情：
1. 字母全部变小写，英文括号转换为中文括号，去掉特殊符号
2. 姓名如果中英文混合，只留中文
3. 单位如果是大学，只保留学校，去掉学院
'''

import re

class Str2Query:
	pat = re.compile(r'^[a-z]+$')
	pat2 = re.compile(r'[a-z]')
	
	@staticmethod
	def prepare(str):
		str = str.lower().replace('(', '（').replace(')', '）').replace('.', '·')
		special = ' _'
		for ch in special:
			str = str.replace(ch, '')
		return str
	
	@staticmethod
	def get_query_name(name):
		name = name.replace('（', '').replace('）', '')
		if Str2Query.pat.match(name):
			return name
		else:
			return Str2Query.pat2.sub('', name)
	
	@staticmethod
	def get_query_aff(aff):
		if aff.find('（') != -1 or aff.find('科学院') != -1:
			return aff
		if aff.find('大学') != -1:
			return aff[:aff.find('大学')+2]
		if aff.find('学院') != -1:
			return aff[:aff.find('学院')+2]
		return aff
	
	@staticmethod
	def get_query(str):
		name, aff = Str2Query.prepare(str).split(',')
		return ' '.join([Str2Query.get_query_name(name), Str2Query.get_query_aff(aff)])