import re
import os
import string
from nltk.tokenize import word_tokenize
from nltk.tokenize import punkt

INDEX_FILE_NAME = 'static\ponyportal\mlp_index.tsv'


def main():
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

            doc_index = index_doc(doc_text)

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
def index_doc(doc):
    tokens = word_tokenize(doc)
    doc_index = {}
    for token in tokens:
        if token in doc_index:
            doc_index[token] += 1
        else:
            doc_index[token] = 1
    return doc_index


def read_index(filename):
    index = {}
    with open(filename, 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[2:]
            posting_dict = {}
            for posting in posting_list:
                posting = posting.split(':')
                posting_dict[posting[0]] = int(posting[1])
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index


if __name__ == "__main__":
    main()
