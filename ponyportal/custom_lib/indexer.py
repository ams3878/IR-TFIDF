import re
import os
import string
from nltk.tokenize import word_tokenize
from .utils import get_index
from .porter import PorterStemmer

INDEX_FILE_NAME = "ponyportal\static\ponyportal\mlp_index.tsv"
STEM_FILE_NAME = "ponyportal\static\ponyportal\mlp_stems.tsv"
POSITIONAL_INDEX_FILE_NAME = "ponyportal\static\ponyportal\mlp_positions.tsv"
BIGRAM_INDEX_FILE_NAME = "ponyportal\static\ponyportal\mlp_bigrams.tsv"
WINDOW_INDEX_FILE_NAME = "ponyportal\static\ponyportal\mmlp_window_index.tsv"
WINDOW_SIZE = 10

def create_index_tsv():
    index = {}
    for filename in os.listdir('./ponyportal/static/episodes'):
        formatted_filename = os.path.join('./ponyportal/static/episodes', filename)
        doc_num = re.search('(\d+)', filename)
        if type(doc_num) is not None:
            doc_num = str(doc_num.group(1))

        with open(formatted_filename, 'r') as html_file:
            doc_text = html_file.read()
            doc_text = clean_text(doc_text)
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

# Creates a tsv containing the index built using non-overlapping windows of size 10
def create_window_index_tsv():
    index = {}

    for filename in os.listdir('./ponyportal/static/episodes'):
        formatted_filename = os.path.join('.\ponyportal\static\episodes', filename)
        doc_num = re.search('(\d+)', filename)
        if type(doc_num) is not None:
            doc_num = str(doc_num.group(1))

        # Open and index the current file
        with open(formatted_filename, 'r') as html_file:
            doc_text = html_file.read()
            doc_text = clean_text(doc_text)

            words = doc_text.split(' ')
            window_index = 0
            for word_index in range(0, len(words), WINDOW_SIZE):
                max_ind = word_index + WINDOW_SIZE
                if max_ind >= len(words):
                    max_ind = len(words)
                doc_index = tokenize_doc(' '.join(words[word_index:max_ind]))

                # merge document index with the corpus index
                for token in doc_index:
                    index_str = doc_num + ':' + str(window_index)
                    if token not in index:
                        index[token] = index_str
                    else:
                        index[token] += ('\t' + index_str)
                window_index += 1

    # Write index to a file
    with open(WINDOW_INDEX_FILE_NAME, 'w') as output_file:
        for key in sorted(index.keys()):
            line = "%s\t%d\t%s\n" % (key, len(index[key].split('\t')), index[key])
            output_file.write(line)

def create_index_tsv_positions():
    doc_index = {}
    for filename in os.listdir('./ponyportal/static/episodes'):
        formatted_filename = os.path.join('.\ponyportal\static\episodes', filename)

        with open(formatted_filename, 'r') as f:
            doc_text = f.read()
            doc_text = clean_text(doc_text)
            tokens = word_tokenize(doc_text)
            for i in range(len(tokens)):
                try:
                    doc_index[tokens[i]].append((filename, i+1))
                except KeyError:
                    doc_index[tokens[i]] = [(filename, i+1)]

    # Write index to a file
    with open(POSITIONAL_INDEX_FILE_NAME, 'w') as output_file:
        for word, pos_list in sorted(doc_index.items()):
            line = word
            for pos in pos_list:
                line += "\t%s:%s" % (pos[0], pos[1])
            line += "\t\n"
            output_file.write(line)




def make_bigrams(pos_index, freq_index, threshold):
    with open(BIGRAM_INDEX_FILE_NAME, 'w') as output_file:
        for word_1 in pos_index:
            bigrams = {}
            for word_2 in pos_index:
                for doc, pos_list in pos_index[word_1].items():
                    if doc in pos_index[word_2].keys():
                        for pos in pos_list:
                            if pos + 1 in pos_index[word_2][doc]:
                                try:
                                    bigrams[word_2] += 1
                                except KeyError:
                                    bigrams[word_2] = 1

            line = word_1
            for word_2, count in bigrams.items():
                freq = 0
                for w, w_count in freq_index[word_1]["docs"].items():
                    freq += int(w_count)
                ratio = count/freq
                if ratio > threshold:
                    line += "\t" + word_2 + ":" + str(ratio)
            line += "\t\n"
            if line != word_1 + "\t\n":
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
    doc = doc.translate(str.maketrans('', '', string.punctuation))
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
