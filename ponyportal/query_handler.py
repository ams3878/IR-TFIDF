import math


def query(query_string, index, query_model):
    if query_model == 'tfidf':
        return tfidf(query_string, index)


def tfidf(query_string, index):
    terms = query_string.split()
    docs = {}
    for i in range(243):
        docs[i+1] = ('None', 0)
    num_docs = len(docs) * 1.0
    doc_sums = {}
    doc_scores = []
    for term in terms:
        idf = math.log((num_docs/int(index[term]['count']))) + 1
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
    doc_scores = sorted(doc_scores, key=lambda tup: tup[1])
    return doc_scores
