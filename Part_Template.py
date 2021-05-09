# SpaCy Imports
import neuralcoref    
import spacy

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

def merge_entities(document):
    with document.retokenize() as retokenizer:
        for entity in document.ents:
            retokenizer.merge(entity)
    return document

def location_pattern(text):

    doc = nlp(text)
    document = merge_entities(doc)
  
    text_selection = []
    index_next_char = -1
  
    for entity in document.ents:
        if(entity.label_ == "GPE"):
            if(index_next_char==-1 or index_next_char == entity.start_char):
                text_selection.append(entity.text)
                index_next_char = entity.end_char + 2
            elif(index_next_char > 0 and index_next_char + 3 < len(text) and (index_next_char + 3 == entity.start_char or index_next_char + 4 == entity.start_char) and (text[index_next_char - 1 : index_next_char + 2] == "and" or text[index_next_char : index_next_char + 3] == "and")):
                text_selection.append("&")
                text_selection.append(entity.text)
                index_next_char = entity.end_char + 2
            else:
                text_selection.append("#")
                text_selection.append(entity.text)
                index_next_char = entity.end_char + 2
  
    remaining_list = []
  
    for i in range(len(text_selection)):
        if(text_selection[i] == "&"):
            remaining_list.append(i)
            remaining_list.append(i+1)
            j = i - 1
            while(j != 0 and text_selection[j+1] != "#"):
                remaining_list.append(j)
                j = j - 1
  
    remaining_list = list(dict.fromkeys(remaining_list))
  
    for index in sorted(remaining_list, reverse=True):
        del text_selection[index]
  
    text_pattern = []
    temp_tuple_pattern = ()
  
    for i in (range(len(text_selection)-1)):
        if(text_selection[i+1] == "#" or text_selection[i] == "#"):
            continue
        else:
            temp_tuple_pattern = (text_selection[i],text_selection[i+1])
            text_pattern.append(temp_tuple_pattern)
  
    return text_pattern
        
def part_template_sentence_check(sentence,ner_sentence):
    
    count = sum((x == 'GPE') for x in ner_sentence.values())
    
    if(count>=2):
        return sentence
    
    return None

def part_home(sentence):
    
    combined_output=set()
    
    combined_output.update(location_pattern(sentence))
    # combined_output.update(holonymn_pattern(sentence))
    
    combined_output = list(combined_output)
    
    return combined_output

def getPart(sentences,ner_list):

    final_part = []
    selected_sentences_list = []
    
    for index,sentence in enumerate(sentences):
        output_sentence = part_template_sentence_check(sentence,ner_list[index])
        if output_sentence is None:
            continue
        else:
            selected_sentences_list.append(output_sentence)
    
    for sentence in selected_sentences_list:
        try:

            part_output = part_home(sentence)

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

    return final_part