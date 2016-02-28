from corpus import *
import numpy as np
import subprocess

class Sieve(object):
	def __init__(self, rootdir):
		self.conll_corpus = Corpus(rootdir)

		self.muc_results = np.zeros(4)
		self.bcub_results = np.zeros(4)
		self.ceafm_results = np.zeros(4)
		self.ceafe_results = np.zeros(4)
		self.blanc_results = np.zeros(4)
		self.all_results = np.zeros(4)

		self.metrics = [('muc', self.muc_results), ('bcub', self.bcub_results), ('ceafm', self.ceafm_results), ('ceafe', self.ceafe_results), ('blanc', self.blanc_results), ('all', self.all_results)]

		shutil.rmtreee('responses') #clear from previous tries
		os.mkdir('responses') #dir to hold response files

	def run_sieve(self):
		"""main function to run all docs through sieve"""

		for doc in self.conll_corpus.documents:
			#each entity starts out as a singleton
			doc.chains = [[ent] for ent in doc.entities]

			######INSERT SIEVES HERE######


			########END SIEVES###########

			self.find_output_ids(doc)
			self.write_response(doc)
			self.score_document(doc)

		self.write_results()

			
	def find_output_ids(self, document):
		"""adds output coreference chain ids to Token objects"""
		for chain in document.chains:
			
	

	def write_response(self, document, fpath):
		"""writes sieve output in conll format to fpath"""
		with open(fpath, 'w') as outfile:
			pass
		

	def score_document(self, document, response_fpath):
		"""runs scorer for all metric and updates results"""
		key_file = document.fpath
		response_file = response_fpath
		scorer_path = 'reference-coference-scorers-8.01/scorer.pl'

		for (metric, result_array) in self.metrics:
			doc_result = subprocess.check_output([scorer_path, metric, key_file, response_file])
			result_array += np.array(doc_result)


	def write_results(self):
		"""write file with final precision/recall/fmeasure"""
		with open('sieve_results.txt', 'w') as resultsfile:
			for (metric, result_array) in self.metrics:
				recall = result_array[0]/result_array[1]
				precision = result_array[2]/result_array[3]
				f1measure = 2 * precision * recall / (precision * recall)
				resultsfile.write('Metric: {}\tPrecision: {}\tRecall: {}\tF1Measure: {}\n'.format(metric, precision, recall, f1measure))

