# NLP - Information Extraction Templates

# Basic Imports
import sys
import re

# SpaCy Imports
import neuralcoref    
import spacy
from spacy.pipeline import EntityRuler

from Part_Template_LOC import location_pattern

nlp = spacy.load('en_core_web_sm')
ruler = EntityRuler(nlp)
patterns = [{"label": "BORN", "pattern": "founded by"}, {"label": "BORN", "pattern": "founded on"}, {"label": "BORN", "pattern": "born on"},{"label": "BORN", "pattern": "founder of"},]
# {"label": "ACQUIRE", "pattern": "bought"}, {"label": "ACQUIRE", "pattern": "bought  by"},{"label": "ACQUIRE", "pattern": "took over"},{"label": "ACQUIRE", "pattern": "owns"},{"label": "ACQUIRE", "pattern": "owned"},{"label": "ACQUIRE", "pattern": "own"},{"label": "ACQUIRE", "pattern": "purchased"}, {"label": "ACQUIRE", "pattern": "purchased by"},]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)
# merge_nps = nlp.create_pipe("merge_noun_chunks")
# nlp.add_pipe(merge_nps)
neuralcoref.add_to_pipe(nlp)

# def entity_check(token,doc):
#     for ent in doc.ents:
#         if token == ent:
#             return True
#     return False

def extraction(sentence,doc,ner_list,dp_list):
    
    template = {"Parameter_1": "", "Date": "", "Location": ""}
    list_of_templates = []
    temp_date=None

    for head in doc:
        for index, token in enumerate(head.children):
            if index == 0:
                cur_token = [token.dep_,token.head.text,token.text,token.pos_]
                prev_token = [token.dep_,token.head.text,token.text,token.pos_]
            else:
                prev_token = cur_token
                cur_token = [token.dep_,token.head.text,token.text,token.pos_]

            if(head.ent_type_=="BORN"):
                count_loc = sum((x == 'GPE') for x in ner_list.values())
                count_date = sum((x == 'DATE') for x in ner_list.values())
                for index,x in enumerate(ner_list):

                    if index == 0:
                        prev_token = [x.label_,x.text]
                        cur_token = [x.label_,x.text]
                    else:
                        prev_token = cur_token
                        cur_token = [x.label_,x.text]
                    if(re.search("(founded by|born on|founder of|founded on)", cur_token[1])):
                        if(prev_token[0]=="ORG" or prev_token[0]=="PERSON"):
                            template["Parameter_1"] = prev_token[1]
                    
                    if(x.label_ == "DATE" and len(template["Date"])==0):
                        # if(count_date == 1):
                        template["Date"] = x.text
                    
                    if(count_loc > 1 and x.label_ == "GPE"):
                        loc = list(location_pattern(sentence))
                        template["Location"] = str(loc[0][0])+", "+ str(loc[0][1])
                    elif(count_loc == 1 and x.label_ == "GPE"):
                        template["Location"] = x.text

    if (len(template["Parameter_1"]) > 0 and len(template["Date"]) > 0):
        list_of_templates.append(template)
        template = {"Parameter_1": "", "Date": "", "Location": ""}

    return list_of_templates

def acquire_relation_check(sentence):
    if(re.search("(acquire|acquires|acquired by)", sentence)):
        return True
    return False

def born_template_sentence_check(sentence,ner_sentence,dp_sentence):

    count_org = sum((x == 'ORG') for x in ner_sentence.values())
    count_person = sum((x == 'PERSON') for x in ner_sentence.values())
    count_date = sum((x == 'DATE') for x in ner_sentence.values())
    count_loc = sum((x == 'GPE') for x in ner_sentence.values())
    if((count_org >=1 or count_person >= 1) and count_date >= 1 and count_loc >= 1):
        # result = acquire_relation_check(sentence)
        # if(result): 
        #     # print(sentence)
        #     # print(ner_sentence)
        #     # print(dp_sentence)
        return sentence

    return sentence

def getBorn(sentences,ners_list,dependency_parse_list):
    final_part=[]
    selected_sentences_list = sentences
    selected_sentences_dependency_parse_structure = dependency_parse_list
    selected_sentences_ner = ners_list
    # for index,sentence in enumerate(sentences):
    #     output_sentence = born_template_sentence_check(sentence,ners_list[index],dependency_parse_list[index])
        
    #     if output_sentence is None:
    #         continue
    #     else:
    #         selected_sentences_ner.append(ners_list[index])
    #         selected_sentences_dependency_parse_structure.append(dependency_parse_list[index])
    #         selected_sentences_list.append(output_sentence)

    for index,sentence_text in enumerate(selected_sentences_list):
        # try:
            sentence = nlp(sentence_text)
            # BORN
            ans = extraction(sentence_text,sentence,selected_sentences_ner[index],selected_sentences_dependency_parse_structure[index])
            if(ans!=[]):
                print(ans)
                for i in ans:

                    temp_dict={}
                    temp_dict["template"]="BORN"
                    temp_dict["sentences"]=[]
                    temp_dict["sentences"].append(sentence.text)
                    temp_dict["arguments"]={}
                    temp_dict["arguments"]["1"]=i["Parameter_1"]
                    temp_dict["arguments"]["2"]=i["Date"]
                    temp_dict["arguments"]["3"]=i["Location"]
                    final_part.append(temp_dict)

    return final_part
    