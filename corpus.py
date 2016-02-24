"""
Initial script to process conll files
If needed: change rootdir at the bottom to run on your machine
This version has sentence objects
"""

import os, re, nltk.tree

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
		#self.*_bits used temporarily for reading in
		self.ne_bit = self.linelist[10] 
		self.arg_bits = self.linelist[11:-1]
		self.coref_bits = self.linelist[-1].split('|')
		self.ne = None
		self.args = []
		self.coref_ids = []
	
class Sentence(object):
	def __init__(self, sent_list, sent_number):
		self.sent_list = sent_list #list of line splits
		self.sent_number = sent_number
		self.tokens = [] #list of Token objects
		self.parse = '' #string to turn into nltk tree
		self.parse_tree = None #nltk tree
		#TODO: create a better way of connecting Token objects to tree nodes
		self.load_tokens()
		self.process_sent()

	def load_tokens(self):
		"""initial token processing"""
		for token_line_split in self.sent_list:
			new_token = Token(token_line_split, self.sent_number)
			self.tokens.append(new_token)

	def process_sent(self):
		"""process features that go across tokens"""
		num_of_args = len(self.tokens[0].arg_bits)
		curr_args = [None for i in range(num_of_args)]
		curr_ne = None
		curr_coref_ids = []

		for t in self.tokens:
			#parse
			parse_string = t.parse_bit.replace('*', '({} {})'.format(t.pos, t.token))
			parse_string = re.sub(r'([A-Z])(\()', r'\1 (', parse_string)
			#if I use an escape character here ^ that ends up in the tree
			parse_string = parse_string.replace(')(', ') (')
			self.parse += parse_string

			#NE type
			if t.ne_bit.startswith('('):
				curr_ne = t.ne_bit.strip('()*')
			t.ne = curr_ne
			if t.ne_bit.endswith(')'):
				curr_ne = None

			#coref ids
			#improve this?
			for bit in t.coref_bits:
				if bit.startswith('('):
					curr_coref_ids.append(bit.strip('()'))
			t.coref_ids.extend(curr_coref_ids)
			for bit in t.coref_bits:
				if bit.endswith(')'):
					curr_coref_ids.remove(bit.strip('()'))

			#args
			for i in range(len(curr_args)):
				if t.arg_bits[i].startswith('('):
					curr_args[i] = t.arg_bits[i].strip('()*')
				t.args.append(curr_args[i])
				if t.arg_bits[i].endswith(')'):
					curr_args[i] = None

			#print 'ne: {}, args: {}, coref: {}'.format(t.ne, t.args, t.coref_ids)
	
		self.parse_tree = nltk.tree.Tree.fromstring(self.parse)
		#print(self.parse_tree)


class Document(object):
	"""reads a single file and creates Sentence objects"""
	def __init__(self, fpath):
		self.fpath = fpath
		self.sentences = [] #list of Sentence objects
		self.load_sents()

	def load_sents(self):
		with open(self.fpath) as conllfile:
			sent_number = 0
			curr_sent_list = []
			for line in conllfile.readlines():
				if line.startswith('#'):
					continue
				elif line == '\n':
					new_sent = Sentence(curr_sent_list, sent_number)
					sent_number += 1
					curr_sent_list = []
				else:
					curr_sent_list.append(line.split())
									
class Corpus(object):
	"""collection of conll files"""
	def __init__(self, rootdir):
		self.rootdir = rootdir
		self.documents = []
		self.load_corpus()

	def load_corpus(self):
		for dirpath, dirs, fnames in os.walk(self.rootdir):
			for f in fnames:
				if f.endswith('auto_conll'):
					fullpath = os.path.join(dirpath, f)
					self.documents.append(Document(fullpath))

if __name__ == '__main__':
	conll_corpus = Corpus('conll-2012/train')
		