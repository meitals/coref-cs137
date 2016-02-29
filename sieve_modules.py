"""Separate modules for earch layer of the sieve"""

import re
from corpus import Document

WRITE_LOG = True
LOGFILE = open("sieve_functions.log","w")

def exact_match(entity_list, coreference_chains):
	"""First pass of the sieve: looks for exact 
	full_string matches"""
	print("Trying exact match")
	chains = []
	for entity in entity_list:
		found_chain = False
		for chain in chains:
			if entity.full_string == chain[0].full_string: # For exact match, assume all are the same
				found_proper = False
				for token in entity.tokens:
					if "NNP" in token.pos: # Don't assume pronouns match
						found_proper = True
						break
				if not found_proper:
					continue
				chain.append(entity)
				found_chain = True
				write_log("Found exact match", entity, chain[0])
				break
		if not found_chain:
			chains.append([entity])
	return chains

def precise_constructs(entity_list, coreference_chains, document):
	chains = []
	for coref_chain in coreference_chains:
		for chain in chains:
			for entity in chain:
				for coref_entity in coref_chain:
					between_tokens, between_words = get_between_tokens(entity, coref_entity, document)
					if between_tokens != None:
						if "NP" in entity.parse_string and "NP" in coref_entity.parse_string:
							if len(between_tokens) <= 1: 
								# Look for role appositives
								if len(between_tokens) == 0 and (entity.ne_type == "PERSON" or coref_entity.ne_type == "PERSON"):
										coref_chain.extend(chain)
										chains.remove(chain)
										write_log("Role appositive",entity,coref_entity)
										continue
								if len(between_tokens) == 1: 
									# Look for appositive constructions
									if between_tokens[0].full_string == ",":
										coref_chain.extend(chain)
										chains.remove(chain)
										write_log("Appositive",entity,coref_entity)
										continue
									# Look for predicate nominatives
									if between_tokens[0].pos == "VBZ" or between_tokens[0].pos == "VBD":
										coref_chain.extend(chain)
										chains.remove(chain)
										write_log("Predicate nominative",entity,coref_entity)
										continue
							if len(between_tokens) > 1:
								# Find relative pronoun constructions
								if "which" or "that" in between_words:
									coref_chain.extend(chain)
									chains.remove(chain)
									write_log("Relative pronouns",entity,coref_entity)
									continue
								if is_acronym(entity, coref_entity):
									coref_chain.extend(chain)
									chains.remove(chain)
									write_log("Acronyms",entity,coref_entity)
									continue
		chains.append(coref_chain)
	return coreference_chains

def get_between_tokens(entity1, entity2, document):
	"""Returns list of tokens between two entities"""
	tokens1 = entity1.tokens
	tokens2 = entity2.tokens
	output = []
	words = []
	if tokens1[0].sent_number == tokens2[0].sent_number:
		sent_number = tokens1.sent_number
		if tokens1[0].token_number <= tokens2[0].token_number:
			if tokens1[-1].token_number >= tokens2[0].token_number: # Entity1 overlaps with entity2
				return [],""
			else:
				for i in range(tokens1[-1],tokens2[0]):
					output.append(document.sentences[sent_number][i].tokens[i])
					words.append(document.sentences[sent_number][i].tokens[i].token)
		elif tokens2[0].token_number <= tokens1[0].token_number:
			if tokens2[-1].token_number >= tokens1[0].token_number: # Entity1 overlaps with entity2
				return [],""
			else:
				for i in range(tokens2[-1],tokens1[0]):
					output.append(document.sentences[sent_number][i].tokens[i])
					words.append(document.sentences[sent_number][i].tokens[i].token)
	else:
		return None
	return output," ".join(words)


def write_log(msg, entity1, entity2):
	if WRITE_LOG:
		LOGFILE.write(msg+"\t"+entity1.full_string+"\t"+entity2.full_string+"\t" +entity1.filename+"\t"+str(entity1.sentence_index)+"\t"+str(entity2.sentence_index)+"\n")


def is_acronym(entity1, entity2):
	"""Returns whether the entity is an acronym from an NE"""
	acronym = []
	for token in entity1.tokens:
		acronym.append(token.token[0])
	acronym = "".join(acronym)
	if acronym == entity2.full_string:
		return True
	else:
		return is_acronym(entity2,entity1)

def demonym(entity_list, coreference_chains):
	"""Doesn't show up often in training files"""
	pass

def cluster_head_match(entity_list, coreference_chains):
	chains = []
	for coref_chain in coreference_chains:
		for chain in chains:
			for coref_entity in coref_chain:
				for entity in chain:
					# Right now use only people to be more precise
					if coref_entity.ne_type == "PERSON" and entity.ne_type == "PERSON":
						if coref_entity.full_string in entity.full_string or entity.full_string in coref_entity.full_string:
							coref_chain.extend(chain)
							chains.remove(chain)
							write_log("Cluster head match",entity,coref_entity)
							continue							
		chains.append(coref_chain)
	return coreference_chains

def word_inclusion(entity_list, coreference_chains):
	pass

def compatible_modifiers(entity_list, coreference_chains):
	pass

