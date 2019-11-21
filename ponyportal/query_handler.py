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
    doc_scores = []

    for doc in docs:
        sum_terms = 0.0
        sum_sq_terms = 0.0
        for term in terms:
            tf = find_term_count(term, index, doc)
            if tf > 0:
                print("found it")
                tf = math.log(tf)
            tf += 1
            idf = find_idf(term, index, num_docs)
            tf_idf = tf*idf
            sum_sq_terms += math.pow(tf_idf, 2)
            sum_terms += tf_idf
        if sum_sq_terms != 0:
            doc_score = sum_terms/(math.sqrt(sum_sq_terms))
        if doc_score != 1:
            doc_scores.append((doc, doc_score))

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
            posting_dict = {}
            for posting in posting_list:
                posting = posting.split(':')
                posting_dict['count'] = str(line[1])
                posting_dict[posting[0]] = int(posting[1])
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index


if __name__ == "__main__":
    main()