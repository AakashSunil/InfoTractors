# NLP - Information Extraction Templates

# Basic Imports
import sys

# SpaCy Imports
import neuralcoref    
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load('en_core_web_sm')
ruler = EntityRuler(nlp)
patterns = [{"label": "ACQUIRE", "pattern": "purchased"}, {"label": "ACQUIRE", "pattern": "purchased by"},
                {"label": "ACQUIRE", "pattern": "acquired by"}, {"label": "ACQUIRE", "pattern": "acquired"},
            {"label": "ACQUIRE", "pattern": "acquire"}, {"label": "ACQUIRE", "pattern": "bought"}, 
            {"label": "ACQUIRE", "pattern": "bought  by"},{"label": "ACQUIRE", "pattern": "took over"},
           {"label": "ACQUIRE", "pattern": "owns"},{"label": "ACQUIRE", "pattern": "owned"},
            {"label": "ACQUIRE", "pattern": "own"}]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)
# merge_nps = nlp.create_pipe("merge_noun_chunks")
# nlp.add_pipe(merge_nps)
neuralcoref.add_to_pipe(nlp)

def extraction(doc):
    template = {"buyer": "", "item": "", "price": "", "quantity": "", "source": ""}
    list_of_templates = []
    
    # A BUY B for MONEY
    for head in doc:
        if(head.ent_type_=="ACQUIRE"):
            for token in head.children:
                if (token.dep_ == "nsubj"):
                    template["buyer"] = token
                if((token.pos_=="NOUN" and token.dep_ == "dobj")):
                    template["item"] = token
                    for j in token.children:
                        if(j.dep_=="nummod"):
                            template["quantity"]=j
                elif (token.dep_ == "dobj"):
                    template["item"] = token
                for i in doc:
                    if(i.ent_type_ == "MONEY"):
                        if(head in list(i.ancestors)):
                            template["price"] = i
                    if(i.text.lower()=="from" or i.text.lower()=="of" or i.text.lower()=="in"):
                        for j in i.children:
                            if(j.pos_=="PROPN" and j.ent_type_!="GPE"):
                                template["source"]=j
                if (len(template["buyer"]) > 0 and len(template["item"]) > 0):
                    list_of_templates.append(template)
                    template = {"buyer": "", "item": "", "price": "", "quantity": "", "source": ""}
    
    # B was BUY by A for MONEY
    
    for head in doc:
        if(head.ent_type_=="ACQUIRE"):
            for token in head.children:
                if((token.pos_=="NOUN" and token.dep_ == "nsubjpass")):
                    template["item"] = token
                    for j in token.children:
                        if(j.dep_=="nummod"):
                            template["quantity"]=j
                elif ( token.dep_ == "nsubjpass"):
                    template["item"] = token
                if ( token.dep_ == "pobj" ):
                    template["buyer"] = token
                
                for i in doc:
                    if(i.ent_type_ == "MONEY"):
                        if(head in list(i.ancestors)):
                            template["price"] = i
                    if(i.text.lower()=="from" or i.text.lower()=="of" or i.text.lower()=="in"):
                        for j in i.children:
                            if(j.pos_=="PROPN" and j.ent_type_!="GPE"):
                                template["source"]=j
                if (len(template["buyer"]) > 0 and len(template["item"]) > 0):
                    list_of_templates.append(template)
                    template = {"buyer": "", "item": "", "price": "", "quantity": "", "source": ""}
    
    return list_of_templates


def getAquire(sentences):
    final_part=[]
    for sentence_text in sentences:
        # try:
            sentence = nlp(sentence_text)
            # sentence=merge_entities(sentence)

            #ACQUIRE
            ans=extraction(sentence)
            if(ans!=[]):
                for i in ans:
                    temp_dict={}
                    temp_dict["template"]="ACQUIRE"
                    temp_dict["sentences"]=[]
                    temp_dict["sentences"].append(sentence.text)
                    temp_dict["arguments"]={}
                    temp_dict["arguments"]["1"]=i["buyer"].text
                    temp_dict["arguments"]["2"]=i["item"].text
                    if(len(i["price"])==0):
                        temp_dict["arguments"]["3"]=i["price"]
                    else:
                        temp_dict["arguments"]["3"]=i["price"].text
                    if(len(i["quantity"])==0):
                        temp_dict["arguments"]["4"]=i["quantity"]
                    else:
                        temp_dict["arguments"]["4"]=i["quantity"].text
                    if(len(i["source"])==0):
                        temp_dict["arguments"]["5"]=i["source"]
                    else:
                        temp_dict["arguments"]["5"]=i["source"].text
                    final_part.append(temp_dict)

    return final_part
    
