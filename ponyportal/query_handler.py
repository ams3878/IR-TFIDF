import math


def main():
    query('twilight sparkle')


def query(query_string):
    terms = query_string.split()

    index = get_index()
    docs = {}
    for i in range(243):
        docs[i+1] = ('None', 0)
    num_docs = len(docs) * 1.0
    doc_sums = {}
    doc_scores = []
    for term in terms:
        idf = find_idf(term, index, num_docs)
        try:
            for doc, frequency in index[term]['docs'].items():
                tf = math.log(frequency + 1)
                tf_idf = tf*idf
                try:
                    doc_sums[doc] = (doc_sums[doc][0] + tf_idf, doc_sums[doc][1] + math.pow(tf_idf, 2))
                except KeyError:
                    doc_sums[doc] = (tf_idf, math.pow(tf_idf, 2))

        except KeyError:
            continue
    for i, sums in doc_sums.items():
        doc_scores.append((i, sums[0]/sums[1]))
    doc_scores = sorted(doc_scores, key=lambda tup: tup[1], reverse=True)
    return doc_scores


def find_idf(term, index, total_docs):
    try:
        index_entry = index[term]
    except KeyError:
        return 0.0
    docs_with_term = len(index_entry) - 1.0
    idf = math.log((total_docs/docs_with_term), 10)
    return idf


def find_term_count(term, index, doc_id):
    try:
        term_entry = index[term]
    except KeyError:
        return 0
    if doc_id not in term_entry:
        return 0
    term_count = term_entry[doc_id]
    return term_count


def get_docs():
    docs = {}
    with open('docNames.tsv', 'r') as doc_file:
        line = doc_file.readline()
        while line:
            line = line.split('\t')
            docs[line[0]] = (line[1], line[2])
            line = doc_file.readline()
    return docs


def get_index():
    index = {}
    with open('ponyportal\static\ponyportal\mlp_index.tsv', 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[2:]
            posting_dict = {'docs': {}}
            for posting in posting_list:
                posting = posting.split(':')
                posting_dict['count'] = str(line[1])
                posting_dict['docs'][posting[0]] = int(posting[1])
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index


if __name__ == "__main__":
    main()