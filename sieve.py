from corpus import *
from sieve_modules import *
import numpy as np
import subprocess, shutil

class Sieve(object):
	def __init__(self, rootdir):
		self.conll_corpus = Corpus(rootdir)

		self.muc_results = np.zeros(4)
		self.bcub_results = np.zeros(4)
		self.ceafm_results = np.zeros(4)
		self.ceafe_results = np.zeros(4)
		self.blanc_results = np.zeros(4)
		#self.all_results = np.zeros(4)

		self.metrics = [('muc', self.muc_results), ('bcub', self.bcub_results), ('ceafm', self.ceafm_results), ('ceafe', self.ceafe_results), ('blanc', self.blanc_results)]

		if os.path.isdir('responses'):
			shutil.rmtree('responses') #clear from responses dir from previous try
		os.mkdir('responses') #create dir to hold response files

	def run_sieve(self):
		"""main function to run all docs through sieve"""

		filenum = 0

		for doc in self.conll_corpus.documents:
			#each entity starts out as a singleton
			doc.chains = [[ent] for ent in doc.entities]
			#print [[ent.full_string] for ent in doc.entities]

			######INSERT SIEVES HERE######
			###sieves modify doc.chains###
			
			doc.chains = exact_match(doc.entities, doc.chains)
			doc.chains = precise_constructs(doc.entities, doc.chains, doc)
			#doc.chains = cluster_head_match(doc.entities, doc.chains)
			
			########END SIEVES###########


			self.find_output(doc)
			response_fpath = 'responses/{}.response'.format(os.path.basename(doc.fpath))
			self.write_response(doc, response_fpath) 
			self.score_document(doc, response_fpath)

		self.write_results()

			
	def find_output(self, document):
		"""adds output coreference chain ids to Token objects"""
		#create BILU tags for tokens corresponding to coref chains
		for chain_id in range(len(document.chains)):
			for entity in document.chains[chain_id]:
				for i in range(len(entity.tokens)):
					if len(entity.tokens) == 1:
						entity.tokens[i].output_ids.append((chain_id, 'U')) #unique	
					elif i == 0:
						entity.tokens[i].output_ids.append((chain_id, 'B')) #begin
					elif i == (len(entity.tokens)-1):
						entity.tokens[i].output_ids.append((chain_id, 'L')) #last
					else:
						entity.tokens[i].output_ids.append((chain_id, 'I')) #inside
						
		#format to write coref chains to response file
		for sent in document.sentences:
			for token in sent.tokens:
				if len(token.output_ids) == 0:
					token.output_coref_string = '-'

				elif len(token.output_ids) == 1:
					#token part of entity that is in one coref chain

					chain_id = token.output_ids[0][0]
					blui_tag = token.output_ids[0][1]

					if blui_tag == 'B':
						token.output_coref_string = '({}'.format(chain_id)
					elif blui_tag == 'I':
						token.output_coref_string = '-'
					elif blui_tag == 'L':
						token.output_coref_string = '{})'.format(chain_id)
					elif blui_tag == 'U':
						token.output_coref_string = '({})'.format(chain_id)
				
				else:
					#token part of entity that is in multiple coref chains
					temp_output_list = []
					for (chain_id, blui_tag) in token.output_ids:
						if blui_tag == 'B':
							temp_output_list.append('({}'.format(chain_id))
						elif blui_tag == 'L':
							temp_output_list.append('{})'.format(chain_id))
						elif blui_tag == 'U':
							temp_output_list.append('({})'.format(chain_id))
					token.output_coref_string = '|'.join(temp_output_list)


	def write_response(self, document, fpath):
		"""writes sieve output in conll format to fpath"""
		with open(fpath, 'w') as outfile:
			
			curr_doc_part = '0'
			outfile.write('#begin document ({}); part 000\n'.format(document.fpath))
			for sent in document.sentences:
				for token in sent.tokens:
					if token.part_number != curr_doc_part:
						outfile.write('#end document\n')
						outfile.write('#begin document ({}); part {}\n'.format(token.filename, token.part_number.zfill(3)))
						curr_doc_part = token.part_number
					outfile.write(' '.join([token.filename, token.part_number, str(token.token_number), token.token, token.output_coref_string]))
					outfile.write('\n')

				outfile.write('\n')


	def result2array(self, result_string):
		result_list = result_string.split()
		rec_num = float(result_list[2][1:])
		rec_denom = float(result_list[4][:-1])
		prec_num = float(result_list[7][1:])
		prec_denom = float(result_list[9][:-1])

		return np.array([rec_num, rec_denom, prec_num, prec_denom])

	def score_document(self, document, response_fpath):
		"""runs scorer for all metric and updates results"""
		key_file = document.fpath
		response_file = response_fpath
		scorer_path = 'project2/reference-coreference-scorers-8.01/scorer.pl'
		result_num = 0

		if os.path.isdir('results'):
			shutil.rmtree('results')
		os.mkdir('results') 

		for (metric, result_array) in self.metrics:
			doc_result = subprocess.check_output([scorer_path, metric, key_file, response_file])
			print(doc_result.split('\n')[-3]) #grab line with overall results
			with open('results/result{}.txt'.format(str(result_num)), 'w') as scorefile:
				scorefile.write(doc_result)
			result_array += self.result2array(doc_result.split('\n')[-3])
			result_num += 1

	def write_results(self):
		"""write file with final precision/recall/fmeasure"""
		with open('sieve_results.txt', 'w') as resultsfile:
			for (metric, result_array) in self.metrics:
				recall = result_array[0]/result_array[1]
				precision = result_array[2]/result_array[3]
				f1measure = 2 * precision * recall / (precision + recall)
				resultsfile.write('Metric: {}\tPrecision: {}\tRecall: {}\tF1Measure: {}\n'.format(metric, precision, recall, f1measure))

if __name__ == '__main__':
	jst_sieve = Sieve('project2/conll-2012/dev')
	jst_sieve.run_sieve()
