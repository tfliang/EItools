import pickle

from EItools.config.globalvar import CLASSIFIER_DIR


class Name:
	with open(CLASSIFIER_DIR+'/data/name2freq.pkl', 'rb') as f:
		name2freq = pickle.load(f)
	@staticmethod
	def iscommon(name, threshold=50):
		if name not in Name.name2freq:
			return False
		if Name.name2freq[name] <= threshold:
			return False
		return True
