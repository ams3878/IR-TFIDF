DOC_INDEX_FILENAME = 'static/ponyportal/mlp_index.tsv'
WINDOW_INDEX_FILENAME = 'static/ponyportal/mlp_window_index.tsv'

def init():
    global index
    global doc_index
    global window_index
    index = build_index()
    doc_index = build_docs_index()
    window_index = build_window_index()

def get_index():
    return index

def get_doc_index():
    return doc_index

def get_window_index():
    return window_index



def build_index():
    index = {}
    with open(DOC_INDEX_FILENAME, 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[2:]
            posting_dict = {'docs': {},
                            'count': str(line[1])}

            for posting in posting_list:
                posting = posting.split(':')

                posting_dict['docs'][posting[0]] = int(posting[1])
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index
