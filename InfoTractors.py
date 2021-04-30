# NLP - Information Extraction Templates

# Basic Imports
import sys
from itertools import chain
import os
import errno
import glob
import json

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


# Template Import
from Part_Template import getPart
from Aquire_Template import getAquire

# --------------- File Read from Text --------------------- #
# Read the whole Text File into a variable
def file_read(input_file):
    f = open(input_file,encoding="ascii",errors="ignore")
    text = f.read()
    # text = nlp(text)
    # print(text)
    f.close()

    return text
    
# ---------- Functions for Features from Input Text ---------------- #

# Sentences Extracted from Paragraphs
def sentence_tokenizer(text):
    sentence_tokens = []
    read_text = nlp(text)
    read_text = read_text._.coref_resolved
    
    sentence_tokens = sent_tokenize(read_text)
    return sentence_tokens

# Words Extracted from a Sentence
def word_tokenizer(sentence):
    return word_tokenize(sentence)

# POS Tags for Words using NLTK POS Taggers
def pos_taggers(word_list):
    return nltk.pos_tag(word_list)

# Tagging POS Tags through the Wordnet Corpus
def wordNet_pos_tagger(nltk_tag):
    # POS Tag start with J - Replace with ADJ
    if nltk_tag.startswith('J'):
        return wn.ADJ
    
    # POS Tag start with V - Replace with VERB
    elif nltk_tag.startswith('V'):
        return wn.VERB
    
    # POS Tag start with N - Replace with NOUN
    elif nltk_tag.startswith('N'):
        return wn.NOUN
    
    # POS Tag start with R - Replace with ADV
    elif nltk_tag.startswith('R'):
        return wn.ADV
    
    # Replace tag with None if no match
    else:          
        return None

def word_stemmatization(words):       
    stemmatize_word = {}
    ps = PorterStemmer()
    for word in words:
        stemmatize_word[word] = ps.stem(word)
    return stemmatize_word


def dependency_parsing(sentence):
    dependency_parsed_tree =[]
    doc = nlp(sentence)
    sent = list(doc.sents)
    for s in sent:
        rootOfSentence = s.root.text
    for token in doc:
        dependency_parsed_tree.append([token.dep_,token.head.text,token.text])
    return dependency_parsed_tree

def named_entity_recognition(sentence):
    ner = {}
    doc = nlp(sentence)
    for X in doc.ents:
        key_entities = ''.join(map(str, X.text))
        ner[X] = X.label_
        
    return ner

def wordnet_features(words):

    # Initializtion of the Wordnet Features Dictionaries
    synonymns = {}
    hypernyms = {}
    hyponyms = {}
    meronyms = {}
    holonyms = {}

    # Looping through Words
    for word in words:
        # Initialization for temporary Lists for each Feature
        temp_synonymns = []
        temp_hypernyms = []
        temp_hyponyms = []
        temp_meronyms = []
        temp_holonyms = []

        # Synsets for the Word (WordNet)
        for i,j in enumerate(wn.synsets(word)):

            # Adding the synonymns to the List
            temp_synonymns.extend(wn.synset(j.name()).lemma_names())
            
            # Adding the hypernymns to the List
            temp_hypernyms.extend(list(chain(*[l.lemma_names() for l in j.hypernyms()])))
            
            # Adding the hyponymns to the List
            temp_hyponyms.extend(list(chain(*[l.lemma_names() for l in j.hyponyms()])))
            
            # Adding the meronymns to the List
            temp_meronyms.extend(list(chain(*[l.lemma_names() for l in j.part_meronyms()])))
            
            # Adding the holonymns to the List
            temp_holonyms.extend(list(chain(*[l.lemma_names() for l in j.part_holonyms()])))
        
        # Adding to the Dictionary
        synonymns[word] = temp_synonymns
        hypernyms[word] = temp_hypernyms
        hyponyms[word] = temp_hyponyms
        meronyms[word] = temp_meronyms
        holonyms[word] = temp_holonyms

    return synonymns,hypernyms,hyponyms,meronyms,holonyms

def lemmatization(word_tokens):
    
    # Initializtion of Lemmas based on Word Tokens (NLTK)
    lemmas = {}
    
    # Looping through the Word Tokens
    for word in word_tokens:     
        # Lemmatize the Word
        lemmas[word] = lemmatizer.lemmatize(word)
    
    return lemmas

def lemmatization_wordnet(wordnet_tagged):

    # Initializtion of Lemmas basd on Wordnet Tagged Words
    lemmas_wordnet = {}

    # Looping through the Wordnet Tagged Words
    for word, tag in wordnet_tagged:
        if tag is None:
            # if there is no available tag, append the token as is
            lemmas_wordnet[word] = []
        else:        
            # else use the tag to lemmatize the token
            lemmas_wordnet[word] = lemmatizer.lemmatize(word, tag)
    
    return lemmas_wordnet

def NLP_Feature_Pipeline(sentence,all_stopwords):

    # Word Tokens from the Sentence without Stop Words

    # word_tokens = [word for word in word_tokenizer(sentence) if not word in all_stopwords]
    word_tokens = word_tokenizer(sentence)

    # Dependency Parsing Tree
    d_parse = dependency_parsing(sentence)

    # Wordnet Features - Synonymns, Hypernymns, Hyponymns, Meronymns, Holonymns
    syn,hyper,hypo,mero,holo = wordnet_features(word_tokens)

    # Stemmatization
    stemmas = word_stemmatization(word_tokens)

    # Attach POS Tags to the Word List
    pos_tagged = pos_taggers(word_tokens)

    # Attaching the Wordnet POS Tags to the NLTK POS tags
    wordnet_tagged = list(map(lambda x: (x[0], wordNet_pos_tagger(x[1])), pos_tagged))

    # Initialization of the Lemmas for a WordNet Tagged Sentence 
    lemmas_wordnet = lemmatization_wordnet(wordnet_tagged)

    # Initialization of the Lemmas for a Sentence
    lemmas = lemmatization(word_tokens)

    # Spacy - Named Entity Recognition for Sentence
    ner = named_entity_recognition(sentence)
    
    return word_tokens,pos_tagged,wordnet_tagged,stemmas,lemmas,lemmas_wordnet,syn,hyper,hypo,mero,holo,d_parse,ner



# ------------------------------------------------------------------------------------------------------------------------------------ #
# ---------------------------------------------------- Main Program---Driver Code ---------------------------------------------------- #
# ------------------------------------------- Task 1 - NLP Features from Input Text File --------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------ #


# Input from Command Line
input_file = sys.argv[1]

# Loading Spacy English Model 
nlp = spacy.load('en_core_web_sm')

# Adding the Neural Coreference Resolution to the Pipeline
neuralcoref.add_to_pipe(nlp)

# Stopwords using the Spacy package
all_stopwords = nlp.Defaults.stop_words

# take out the 'not' stopword from the default list as not is an important stopword that can alter meaning if not included
all_stopwords.remove('not')

# Initialization of Lists - Words, POS_Tags, Wordnet Tagged and Lemmatized Sentence Lists
words_list=[]
pos_tag_list = []
wordnet_tagged_list = []
stemmas_list = []
lemmas_list = []
lemmas_wordnet_list = []
synonymns_list = []
hypernyms_list = []
hyponyms_list = []
meronyms_list = []
holonyms_list = []
dependency_parse_tree_list = []
ners_list = []

# Wordnet Lematizer Initialization
lemmatizer = WordNetLemmatizer()

# Text File Read
text_data = file_read(input_file)

# Sentence Tokenizer
sentences = sentence_tokenizer(text_data)

# Getting the features in each sentence - Loop Sentence by Sentence
for sentence in sentences:

    # NLP Pipeline to extract all features - Sentence by Sentence
    word_tokens,pos_tagged,wordnet_tagged,stemma_list,lemmas,lemmas_wordnet,synonymn_list,hypernym_list,hyponym_list,meronym_list,holonym_list,dependency_parse_tree,ner_list = NLP_Feature_Pipeline(sentence,all_stopwords)

    # Appending the Features to Individual Lists
    words_list.append(word_tokens)
    pos_tag_list.append(pos_tagged)
    wordnet_tagged_list.append(wordnet_tagged)
    stemmas_list.append(stemma_list)
    lemmas_list.append(lemmas)
    lemmas_wordnet_list.append(lemmas_wordnet)
    synonymns_list.append(synonymn_list)
    hypernyms_list.append(hypernym_list)
    hyponyms_list.append(hyponym_list)
    meronyms_list.append(meronym_list)
    holonyms_list.append(holonym_list)
    dependency_parse_tree_list.append(dependency_parse_tree)
    ners_list.append(ner_list)

# --------------------------------- Output Features -------------------------------------- #

# Getting the File Name from the Path
base = os.path.basename(input_file)
output_file_name = os.path.splitext(base)[0]

# Create the Features Folder with TextFile Folder
try:
    os.makedirs('Features/'+ output_file_name)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Printing to Files
with open('Features/'+output_file_name+'/'+output_file_name+'_Word_Tokens.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in words_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_POS_Tags.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in pos_tag_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_Stemmas.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in stemmas_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_Lemmas.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in lemmas_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_Lemmas_WordNet.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in lemmas_wordnet_list)

with open('Features/'+output_file_name+'/'+output_file_name+'_Dependency_Parse_Tree.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in dependency_parse_tree_list)


with open('Features/'+output_file_name+'/'+output_file_name+'_synonyms.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in synonymns_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_hypernymns.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in hypernyms_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_hyponymns.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in hyponyms_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_meronymns.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in meronyms_list)
with open('Features/'+output_file_name+'/'+output_file_name+'_holonymns.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in holonyms_list)

with open('Features/'+output_file_name+'/'+output_file_name+'_NER.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in ners_list)


print('\n\nFeatures Found from the Text and Printed on Individual Files in the Features/'+output_file_name+' Folder')
input('Press Any Key to move to Task 2')
print('\nStarting Task 2 - Extract Information Templates using Heuristic, or Statistical or Both Methods\n')

# ------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------- Task 2 - Extract Information Templates using Heuristic, or Statistical or Both Methods ------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------ #

files_list = glob.glob('WikipediaArticles\*.txt')
for file_name in files_list:
    
    text_data = file_read(file_name)
    sentences = sentence_tokenizer(text_data)
    
    output_part_template = getPart(sentences)
    output_acquire_template = getAquire(sentences)

    # Getting the File Name from the Path
    base_name = os.path.basename(file_name)
    output_file_name = os.path.splitext(base_name)[0]

    final_output_dictionary={}
    final_output_dictionary["document"]=base_name
    final_output_dictionary["extraction"]=[]

    for acquire_templates in output_acquire_template:
        final_output_dictionary['extraction'].append(acquire_templates)
        
    for part_templates in output_part_template:
        final_output_dictionary['extraction'].append(part_templates)

    # Create the Features Folder with TextFile Folder
    try:
        os.makedirs('Output_JSONs/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    json_output_file_name = "Output_" + output_file_name + ".json"
    json_object_output = json.loads(json.dumps(final_output_dictionary))
    final_json_data = json.dumps(json_object_output, indent=2)

    output_file = open('Output_JSONs/'+json_output_file_name, "w")
    output_file.write(final_json_data)
    output_file.close()

    print('Output JSON for "' + base_name + '" created in the Output_JSONs Folder - File Name: ' + json_output_file_name)
    # input('Next?')

print('\nTemplate Extraction Completed\n')