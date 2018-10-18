import json

from EItools.config.globalvar import CLASSIFIER_DIR
from .TextSlicer import TextSlicer

class Extract:
	name_slicer = None
	aff_slicer = None
	position_slicer=None
	title_slicer=None
	soc_position_slicer = None
	def init():
		name = set()
		with open(CLASSIFIER_DIR+'/data/name.txt', 'r', encoding = 'utf-8') as f:
			for line in f:
				name.add(line[:-1])
		Extract.name_slicer = TextSlicer(name)
		aff = set()
		with open(CLASSIFIER_DIR+'/data/aff.txt', 'r', encoding = 'utf-8') as f:
			for line in f:
				aff.add(line[:-1])
		Extract.aff_slicer = TextSlicer(aff)
		position=set()
		with open(CLASSIFIER_DIR+'/data/position.json', 'r', encoding = 'utf-8') as f:
			position_list=json.load(f)
			position=set(position_list)
		Extract.position_slicer = TextSlicer(position)
		soc_position = set()
		with open(CLASSIFIER_DIR + '/data/soc_position.json', 'r', encoding='utf-8') as f:
			soc_position_list = json.load(f)
			soc_position = set(soc_position_list)
		Extract.soc_position_slicer = TextSlicer(soc_position)
		title = set()
		with open(CLASSIFIER_DIR + '/data/title.json', 'r', encoding='utf-8') as f:
			title_list = json.load(f)
			title = set(title_list)
		Extract.title_slicer = TextSlicer(title)
	
	def extract_name(str, block = None):
		li = Extract.name_slicer.slice_prob(str)
		nli = []
		for x in li:
			if block is None or x != block:
				nli.append(x)
		return nli
		
	def extract_aff(str, block = None):
		li = Extract.aff_slicer.slice_prob(str)
		nli = []
		for x in li:
			if block is None or len(block.findall(x)) == 0:
				nli.append(x)
		return nli
	def extrac_position(str,block=None):
		li=Extract.position_slicer.slice_prob(str)
		nli=[]
		for x in li:
			if block is None or len(block.findall(x)) == 0:
				nli.append(x)
		return nli
	def extract_soc_position(str,block=None):
		li = Extract.soc_position_slicer.slice_prob(str)
		nli = []
		for x in li:
			if block is None or len(block.findall(x)) == 0:
				nli.append(x)
		return nli
	def extrac_title(str,block=None):
		li=Extract.position_slicer.slice_prob(str)
		nli=[]
		for x in li:
			if block is None or len(block.findall(x)) == 0:
				nli.append(x)
		return nli

