import jieba

class TextSlicer:
	'''
	分词器，只提供最基本的分词功能，其他的过滤停用词等等都分离出去了。
	'''
	def __init__(self, dic):
		self.dic = dic

	def choose(self, universe, parts, start, end):
		if start < 0 or end < 0 or start >= len(universe) or end >= len(universe) \
				or not parts:
			return []
		c = {len(word): (word, i, j) for word, i, j in parts}
		w, i, j = c[max(c.keys())]
		partial_parts_left = list(filter(lambda x: x[1] < i and x[2] < i, parts))
		partial_parts_right = list(filter(lambda x: x[1] > j and x[2] > j, parts))
		partial_res_left = self.choose(universe, partial_parts_left, start, i - 1)
		partial_res_right = self.choose(universe, partial_parts_right, j + 1, end)
		return partial_res_left + [w] + partial_res_right

	def slice_prob(self, text):
		'''
		概率最大算法，认为长词概率更大，效果确实比greedy好，但是复杂度太高了，最坏情况下O(n^3)，最好情况O(n^2 logn)
		因此使用的时候一定要传入短文本，为了保证这一点，函数内部也对文本先用换行符进行分割了
		'''
		text = list(jieba.cut(text.lower()))
		words = []
		parts = []
		for i in range(len(text) + 1):
			for j in range(i + 1, len(text) + 1):
			# for j in range(i + 2, min(len(text) + 1, i + 20)):
			# 如果换成上面这一行，可以限制词的最长长度
				w = ''.join(text[i: j])
				if w in self.dic:
					parts.append((w, i, j - 1))
		words += self.choose(text, parts, 0, len(text) - 1)
		return words
	