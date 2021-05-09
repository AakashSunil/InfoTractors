# NLTK Imports
from nltk import Tree
import re

# SpaCy Imports
import neuralcoref    
import spacy

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

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
    
def part_template_sentence_check(sentence,ner_sentence):

    count = sum((x == 'ORG') for x in ner_sentence.values())

    if(count>=2):
        result = part_of_relation_check(sentence)
        if(result): 
            return sentence

    return None

def display_tree(sentence):

    doc = nlp(sentence)
    [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

def part_home(sentence):
    combined_output=set()
    combined_output.update(organization_pattern(sentence))
    combined_output = list(combined_output)
    return combined_output

def getPartOrg(sentences,ners_list,dependency_parse_list):
    
    final_part = []
    selected_sentences_list = []
    selected_sentences_dependency_parse_structure = []

    for index,sentence in enumerate(sentences):
        output_sentence = part_template_sentence_check(sentence,ners_list[index])
        if output_sentence is None:
            continue
        else:
            selected_sentences_dependency_parse_structure.append(dependency_parse_list[index])
            selected_sentences_list.append(output_sentence)

    final_part = selected_sentences_list
    
    
    # for sentence in selected_sentences_list:
    #     try:
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