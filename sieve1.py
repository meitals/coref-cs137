from corpus import *

def write_response(document):
	pass

def score_doc(document):
	pass

def run_sieve(rootdir):
	conll_corpus = Corpus(rootdir)

	for doc in conll_corpus.documents:
		doc.entities = [[ent] for ent in doc.entities]

		###INSERT SIEVES HERE####


		###END SIEVES###

		###WRITE FILE TO CONLL FORMAT
		

		###SCORE




