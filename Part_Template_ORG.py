# NLTK Imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import Tree
import re

try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/wordnet')
    from nltk.corpus import wordnet as wn

except:
    nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

# SpaCy Imports
import neuralcoref    
import spacy
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc

# import InfoTractors as IT
nlp = spacy.load('en_core_web_sm')

def named_entity_recognition(sentence):
    nlp = spacy.load('en_core_web_sm')
    ner = {}
    doc = nlp(sentence)
    for X in doc.ents:
        key_entities = ''.join(map(str, X.text))
        ner[X] = X.label_
        
    return ner

def merge_entities(document):
    with document.retokenize() as retokenizer:
        for entity in document.ents:
            retokenizer.merge(entity)
    return document

def dependency_parsing(sentence):
    dependency_parsed_tree =[]
    doc = nlp(sentence)
    sent = list(doc.sents)
    for s in sent:
        rootOfSentence = s.root.text
    for token in doc:
        dependency_parsed_tree.append([token.dep_,token.head.text,token.text])
    return dependency_parsed_tree
        
def part_of_relation_check(sentence):
    if(re.search("part of", sentence)):
        return True
    return False

def tok_format(tok):
    return "_".join([tok.orth_, tok.tag_])


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)
    
def part_template_sentence_check(sentence):
    ner_sentence = named_entity_recognition(sentence)
    count = sum((x == 'ORG') for x in ner_sentence.values())
    if(count>=2):
        # return sentence
        result = part_of_relation_check(sentence)
        if(result): 
            return sentence
    return None

def display_tree(sentence):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(sentence)

    [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
    input('a')
    # sent = list(doc.sents)
    # for s in sent:
    #     rootOfSentence = s.root.text
    # for token in doc:
    #     dependency_parsed_tree.append([token.dep_,token.head.text,token.text])
    # return dependency_parsed_tree

def part_home(sentence):
    combined_output=set()
    combined_output.update(organization_pattern(sentence))
    combined_output = list(combined_output)
    return combined_output

def getPartOrg(sentences):
    nlp = spacy.load('en_core_web_sm')
    neuralcoref.add_to_pipe(nlp)
    final_part = []
    selected_sentences_list = []
    for sentence in sentences:
        output_sentence = part_template_sentence_check(sentence)
        if output_sentence is None:
            continue
        else:
            selected_sentences_list.append(output_sentence)

    final_part = selected_sentences_list
    
    
    # for sentence in selected_sentences_list:
    #     try:
    #         # sentence = IT.nlp(sent)
    #         # sentence = IT.merge_entities(sentence)
    #         part_output = part_home(sentence)
    #         # print(part_output)
    #         if(part_output != []):
    #             for j in part_output:
    #                 temp_dict ={}
    #                 temp_dict["template"] ="PART"
    #                 temp_dict["sentences"] = []
    #                 temp_dict["sentences"].append(sentence)
    #                 temp_dict["arguments"] = {}
    #                 temp_dict["arguments"]["1"] = j[0]
    #                 temp_dict["arguments"]["2"] = j[1]
    #                 final_part.append(temp_dict)
    #     except:
    #         continue    
    # print(final_part)
    return final_part