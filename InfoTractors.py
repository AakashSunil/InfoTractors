# NLP - Information Extraction Templates

# Basic Imports
import sys
import glob

from Features import Features_Extraction
from Template_Extraction import task_2_template_extraction

# ------------------------------------------------------------------------------------------------------------------------------------ #
# ---------------------------------------------------- Main Program---Driver Code ---------------------------------------------------- #
# ------------------------------------------- Task 1 - NLP Features from Input Text File --------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------ #
if(len(sys.argv) < 2):

    
    input_file = sys.argv[1]
    sentences,words_list,pos_tag_list,wordnet_tagged_list,stemmas_list,lemmas_list,lemmas_wordnet_list,synonymns_list,hypernyms_list,hyponyms_list,meronyms_list,holonyms_list,dependency_parse_tree_list,ners_list = Features_Extraction(input_file)


# ------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------- Task 2 - Extract Information Templates using Heuristic, or Statistical or Both Methods ------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------ #

task_2_template_extraction(sentences,dependency_parse_tree_list,ners_list,input_file)

print('\nTemplate Extraction Completed\n')