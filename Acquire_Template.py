# NLP - Information Extraction Templates

# Basic Imports
import sys
import re

# SpaCy Imports
import neuralcoref    
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load('en_core_web_sm')
ruler = EntityRuler(nlp)
patterns = [{"label": "ACQUIRE", "pattern": "acquired by"}, {"label": "ACQUIRE", "pattern": "acquired"},{"label": "ACQUIRE", "pattern": "acquire"},]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)
neuralcoref.add_to_pipe(nlp)

def extraction(doc,ner_list,dp_list):
    template = {"Organization 1": "", "Organization 2": "", "Date": ""}
    list_of_templates = []
    temp_date=None
    for head in doc:

        count_date = sum((x == 'DATE') for x in ner_list.values())
        if(count_date == 1 and head.ent_type_=="DATE"):
            temp_date = head
        
        if(head.ent_type_=="ACQUIRE"):
            
            for token in head.children:
                if (token.dep_ == "nsubj"):
                    template["Organization 1"] = token
                if((token.pos_=="NOUN" and token.dep_ == "dobj")):
                    template["Organization 2"] =  token
                elif (token.dep_ == "dobj"):
                    template["Organization 2"] = token
                if(temp_date != None):
                    template["Date"] = temp_date
                elif(head.dep_=="pobj" and head.head.text == "in"):
                    template["Date"] = token
                else:
                    for index,x in enumerate(ner_list):
                        if(x.label_ == "DATE" and len(template["Date"])==0):
                            # if(count_date == 1):
                            template["Date"] = x.text
                if (len(template["Organization 1"]) > 0 and len(template["Organization 2"]) > 0 ):
                    list_of_templates.append(template)
                    template = {"Organization 1": "", "Organization 2": "", "Date": ""}
    
    for head in doc:
        count_date = sum((x == 'DATE') for x in ner_list.values())
        if(count_date == 1 and head.ent_type_=="DATE"):
            temp_date = head
        
        if(head.ent_type_=="ACQUIRE"):
            
            for token in head.children:
                if((token.pos_=="NOUN" and token.dep_ == "nsubjpass")):
                    template["Organization 2"] = token
                elif ( token.dep_ == "nsubjpass"):
                    template["Organization 2"] = token
                if ( token.dep_ == "pobj" ):
                    template["Organization 1"] = token
                if(temp_date != None):
                        template["Date"] = temp_date
                elif(head.dep_=="pobj" and head.head.text == "in"):
                        template["Date"] = token
                else:
                    for index,x in enumerate(ner_list):
                        if(x.label_ == "DATE" and len(template["Date"])==0):
                            # if(count_date == 1):
                            template["Date"] = x.text
                if (len(template["Organization 1"]) > 0 and len(template["Organization 2"]) > 0 ):
                    list_of_templates.append(template)
                    template = {"Organization 1": "", "Organization 2": "", "Date": ""}

    return list_of_templates

def acquire_relation_check(sentence):
    if(re.search("(acquire|acquires|acquired by)", sentence)):
        return True
    return False

def acquire_template_sentence_check(sentence,ner_sentence,dp_sentence):

    count_org = sum((x == 'ORG') for x in ner_sentence.values())
    count_date = sum((x == 'DATE') for x in ner_sentence.values())
    if(count_org >=2 and count_date>=1):
        return sentence

    return None

def getAquire(sentences,ners_list,dependency_parse_list):
    final_part=[]
    selected_sentences_list = []
    selected_sentences_dependency_parse_structure = []
    selected_sentences_ner = []
    for index,sentence in enumerate(sentences):
        output_sentence = acquire_template_sentence_check(sentence,ners_list[index],dependency_parse_list[index])
        
        if output_sentence is None:
            continue
        else:
            selected_sentences_ner.append(ners_list[index])
            selected_sentences_dependency_parse_structure.append(dependency_parse_list[index])
            selected_sentences_list.append(output_sentence)

    for index,sentence_text in enumerate(selected_sentences_list):
        try:
            sentence = nlp(sentence_text)

            # ACQUIRE
            ans = extraction(sentence,selected_sentences_ner[index],selected_sentences_dependency_parse_structure[index])
            if(ans!=[]):
                for i in ans:
                    temp_dict={}
                    temp_dict["template"]="ACQUIRE"
                    temp_dict["sentences"]=[]
                    temp_dict["sentences"].append(sentence.text)
                    temp_dict["arguments"]={}
                    temp_dict["arguments"]["1"]=i["Organization 1"].text
                    temp_dict["arguments"]["2"]=i["Organization 2"].text
                    if(len(i['Date']) == 0):
                        temp_dict["arguments"]["3"]=""
                    else:
                        temp_dict["arguments"]["3"]=i["Date"].text
                   
                    final_part.append(temp_dict)
        except:
            continue
    return final_part
    
