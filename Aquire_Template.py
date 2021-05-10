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
patterns = [{"label": "ACQUIRE", "pattern": "acquired by"}, {"label": "ACQUIRE", "pattern": "acquired"},{"label": "ACQUIRE", "pattern": "acquire"}, {"label": "ACQUIRE", "pattern": "bought"}, {"label": "ACQUIRE", "pattern": "bought  by"},{"label": "ACQUIRE", "pattern": "took over"},{"label": "ACQUIRE", "pattern": "owns"},{"label": "ACQUIRE", "pattern": "owned"},{"label": "ACQUIRE", "pattern": "own"},{"label": "ACQUIRE", "pattern": "purchased"}, {"label": "ACQUIRE", "pattern": "purchased by"},]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)
# merge_nps = nlp.create_pipe("merge_noun_chunks")
# nlp.add_pipe(merge_nps)
neuralcoref.add_to_pipe(nlp)

def entity_check(token,doc):
    for ent in doc.ents:
        if token == ent:
            return True
    return False
def extraction(doc,ner_list,dp_list):
    template = {"Organization 1": "", "Organization 2": "", "Date": ""}
    list_of_templates = []
    temp_date=None
    # print(dp_list)
    
    # print(ner_list)
    for head in doc:
        # for head_check in head:
            
            # print(head_check.text,head_check.head.text,head_check.tag_,head_check.dep_)

        # print(head.ent_type_)
        count_date = sum((x == 'DATE') for x in ner_list.values())
        if(count_date == 1 and head.ent_type_=="DATE"):
            temp_date = head
        
        if(head.ent_type_=="ACQUIRE"):
            # root = doc.root
            
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
                if (len(template["Organization 1"]) > 0 and len(template["Organization 2"]) > 0 ):
                    list_of_templates.append(template)
                    template = {"Organization 1": "", "Organization 2": "", "Date": ""}
    
    # B was BUY by A for MONEY
    
    # for head in doc:
        # print(head)
        # for token in head.children:
        #     if((token.pos_=="NOUN" and token.dep_ == "nsubjpass")):
        #         print(ner_list)
        #         input('b')
        #         template["item"] = token
        #         for j in token.children:
        #             if(j.dep_=="nummod"):
        #                 template["quantity"]=j
        #     elif ( token.dep_ == "nsubjpass"):
        #         template["item"] = token
        #     if ( token.dep_ == "pobj" ):
        #         template["buyer"] = token
            
        #     for i in doc:
        #         if(i.ent_type_ == "MONEY"):
        #             if(head in list(i.ancestors)):
        #                 template["price"] = i
        #         if(i.text.lower()=="from" or i.text.lower()=="of" or i.text.lower()=="in"):
        #             for j in i.children:
        #                 if(j.pos_=="PROPN" and j.ent_type_!="GPE"):
        #                     template["source"]=j
        #     if (len(template["buyer"]) > 0 and len(template["item"]) > 0):
        #         list_of_templates.append(template)
        #         template = {"buyer": "", "item": "", "price": "", "quantity": "", "source": ""}
    return list_of_templates

def acquire_relation_check(sentence):
    if(re.search("(acquire|acquires|acquired by)", sentence)):
        return True
    return False

def acquire_template_sentence_check(sentence,ner_sentence,dp_sentence):

    count_org = sum((x == 'ORG') for x in ner_sentence.values())
    count_date = sum((x == 'DATE') for x in ner_sentence.values())
    if(count_org >=2 and count_date>=1):
        # result = acquire_relation_check(sentence)
        # if(result): 
        #     # print(sentence)
        #     # print(ner_sentence)
        #     # print(dp_sentence)
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

    # for sent in selected_sentences_list:
    #     print(sent)
    for index,sentence_text in enumerate(selected_sentences_list):
        # try:
            sentence = nlp(sentence_text)
            # sentence=merge_entities(sentence)

            #ACQUIRE
            ans=extraction(sentence,selected_sentences_ner[index],selected_sentences_dependency_parse_structure[index])
            if(ans!=[]):
                print(ans)
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

    return final_part
    
