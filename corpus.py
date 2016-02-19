"""
Initial script to process conll files
If needed: change rootdir at the bottom to run on your machine
"""

import os

class Token(object):
	"""all the attributes for a single line in a conll file"""
	def __init__(self, linelist, sent_number):
		self.linelist = linelist
		self.sent_number = sent_number
		self.filename = self.linelist[0]
		self.part_number = self.linelist[1]
		self.token_number = self.linelist[2]
		self.token = self.linelist[3]
		self.pos = self.linelist[4]
		self.parse_bit = self.linelist[5]
		self.lemma = self.linelist[6]
		self.frameset_id = self.linelist[7]
		self.sense = self.linelist[8]
		self.author = self.linelist[9]
		self.ne_bit = self.linelist[10]
		self.args = self.linelist[11:-1]
		self.coref_id = self.linelist[-1]
	
class Document(object):
	def __init__(self, fpath):
		self.fpath = fpath
		self.tokens = [] #list of Token objects
		self.sentences = {} #key: sent number, value: list of Tokens
		#Included self.sentences to make it easier to process parse, args, etc
		self.load()
		#self.process_all_sents()

	def load(self):
		with open(self.fpath) as conllfile:
			sent_number = -1
			for line in conllfile.readlines():
				if line.startswith('#') or line=='\n':
					continue
				else:
					linelist = line.split()
					if linelist[5].startswith('(TOP'):
						sent_number += 1
						self.sentences[sent_number] = []
					newtoken = Token(linelist, sent_number)
					self.tokens.append(newtoken)
					self.sentences[sent_number].append(newtoken)
					print newtoken.pos

	def process_sent(self, tokenlist):
		"""TODO: process all the features that go across Tokens 

		includes: NE type, parse, args, coref chain"""
		pass

	def process_all_sents(self):
		for sent in self.sentences.values():
			process_sent(sent)
		
class Corpus(object):
	"""collection of conll files"""
	def __init__(self, rootdir):
		self.rootdir = rootdir
		self.documents = []
		self.load_corpus()

	def load_corpus(self):
		for dirpath, dirs, fnames in os.walk(self.rootdir):
			for f in fnames:
				if f.endswith('conll'):
					fullpath = os.path.join(dirpath, f)
					self.documents.append(Document(fullpath))

if __name__ == '__main__':
	conll_corpus = Corpus('conll-2012')
		