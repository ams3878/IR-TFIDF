import re
import os
import string
from nltk.tokenize import word_tokenize
from .utils import get_index
from .porter import PorterStemmer

INDEX_FILE_NAME = "ponyportal\static\ponyportal\mlp_index.tsv"
STEM_FILE_NAME = "ponyportal\static\ponyportal\mlp_stems.tsv"

def create_index_tsv():
    index = {}
    for filename in os.listdir('./static/episodes'):
        formatted_filename = os.path.join('./static/episodes', filename)
        doc_num = re.search('(\d+)', filename)
        if type(doc_num) is not None:
            doc_num = str(doc_num.group(1))

        with open(formatted_filename, 'r') as html_file:
            doc_text = html_file.read()
            doc_text = clean_text(doc_text)

            words = doc_text.split(' ')

            doc_index = tokenize_doc(doc_text)

            for token in doc_index:
                index_str = doc_num + ':' + str(doc_index[token])
                if token not in index:
                    index[token] = index_str
                else:
                    index[token] += ('\t' + index_str)

    # Write index to a file
    with open(INDEX_FILE_NAME, 'w') as output_file:
        for key in sorted(index.keys()):
            line = "%s\t%d\t%s\n" % (key, len(index[key].split('\t')), index[key])
            output_file.write(line)


def create_stems(index_tsv):
    vocab = list(get_index(index_tsv).keys())
    stemmer = PorterStemmer()
    stems = [stemmer.stem(word) for word in vocab]
    stem_dict = {}
    for i in range(len(stems)):
        try:
            stem_dict[stems[i]].append(vocab[i])
        except KeyError:
            stem_dict[stems[i]] = [vocab[i]]
    with open(STEM_FILE_NAME, 'w') as f:
        for stem, word_list in sorted(stem_dict.items()):
            if len(word_list) > 1:
                line = "/" + stem
                for word in word_list:
                    line = line + "\t" + word
                line = line + "\t\n"
                f.write(line)

"""
Removes the surrounding <html> and <pre> tags and makes the document lowercase.
"""
def clean_text(doc):
    doc = doc.lower()
    doc = doc.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    return doc


"""
Tokenizes the words in a document then returns a dictionary from each word to its number of occurances in the doc
"""
def tokenize_doc(doc):
    tokens = word_tokenize(doc)
    doc_index = {}
    for token in tokens:
        if token in doc_index:
            doc_index[token] += 1
        else:
            doc_index[token] = 1
    return doc_index
