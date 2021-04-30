# NLTK Imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

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

def location_pattern(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    doc = merge_entities(doc)
    ans=[]
    next_ind=-1
    for ent in doc.ents:
        if(ent.label_ == "GPE"):
            if(next_ind==-1 or next_ind==ent.start_char):
                ans.append(ent.text)
                next_ind=ent.end_char+2
            elif(next_ind>0 and next_ind+3<len(text) and (next_ind+3==ent.start_char or next_ind+4==ent.start_char) and (text[next_ind-1:next_ind+2]=="and" or text[next_ind:next_ind+3]=="and")):
                ans.append("&")
                ans.append(ent.text)
                next_ind=ent.end_char+2;
            else:
                ans.append("#")
                ans.append(ent.text)
                next_ind=ent.end_char+2;
    rem_list=[]
    for i in range(len(ans)):
        if(ans[i]=="&"):
            rem_list.append(i)
            rem_list.append(i+1)
            j=i-1
            while(j!=0 and ans[j+1]!="#"):
                rem_list.append(j)
                j=j-1
    rem_list = list(dict.fromkeys(rem_list))
    for index in sorted(rem_list, reverse=True):
        del ans[index]
    ans_regex=[]
    temp_tup=()
    for i in (range(len(ans)-1)):
        if(ans[i+1]=="#" or ans[i]=="#"):
            continue
        else:
            temp_tup=(ans[i],ans[i+1])
            ans_regex.append(temp_tup)
    return ans_regex
        
def part_template_sentence_check(sentence):
    ner_sentence = named_entity_recognition(sentence)
    count = sum((x == 'GPE') for x in ner_sentence.values())
    if(count>=2):
        return sentence
    return None

def part_home(sentence):
    combined_output=set()
    combined_output.update(location_pattern(sentence))
    # combined_output.update(holonymn_pattern(sentence))
    # combined_output.update(dependency_parse_pattern(sentence))
    combined_output = list(combined_output)
    return combined_output

def getPart(sentences):
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
    for sentence in selected_sentences_list:
        try:
            # sentence = IT.nlp(sent)
            # sentence = IT.merge_entities(sentence)
            part_output = part_home(sentence)
            # print(part_output)
            if(part_output != []):
                for j in part_output:
                    temp_dict ={}
                    temp_dict["template"] ="PART"
                    temp_dict["sentences"] = []
                    temp_dict["sentences"].append(sentence)
                    temp_dict["arguments"] = {}
                    temp_dict["arguments"]["1"] = j[0]
                    temp_dict["arguments"]["2"] = j[1]
                    final_part.append(temp_dict)
        except:
            continue    
    # print(final_part)
    return final_part