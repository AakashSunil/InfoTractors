# InfoTractors

NLP Project to extract different template information from text articles

Program takes input from command line and returns a JSON format of the identified templates.
From the Command Line the File Path of the Text File is passed as argument

Environment and packages --> 
1. python 3.7.9 (neuralcoref works with python 3.7 and below)
2. spacy 2.1.0
3. en_core_web_sm-2.1.0
4. neuralcoref 4.0
5. nltk 3.6.2

Requirements mentioned in requirements.txt

Before Starting the code run the requirements text file to install required packages

    pip install -r requirements.txt

The Folder of the Project consists the following

1. Program (InfoTractors.py) to run the Tasks - Feature Extraction and Template Extraction
2. One folder with all text file articles.
3. requirements.txt file to install the required packages
4. Readme File containing how to run the program.
5. A sample JSON File which contains the sample output.

Program Name: InfoTractors.py
To run the code

    python InfoTractors.py Amazon_com.txt

Expected Output -->
1. One New Folder named 'Features' is created inside which a individual articles have thier respective folders with individual text files for different types of features
2. An Output JSON File with identified templates as per the Sample JSON File Stored in another Folder named 'Output_JSONs'