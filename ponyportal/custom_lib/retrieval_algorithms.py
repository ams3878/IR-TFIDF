import math


def query(query_string, index, query_model):
    if query_model == 'tfidf':
        return tfidf(query_string, index)


def tfidf(terms, index):
    doc_sums = {}
    doc_scores = []
    prev_idf_sqrs = []
    for term in terms:
        try:
            #idf = (num_docs*num_docs*num_docs) / (int(index[term]['count'])/2)
            idf = math.log(244 / int(index[term]['count']))
            for doc, frequency in index[term]['docs'].items():
                tf = math.log(frequency+1)
                tf_idf = tf*idf
                sqrs = tf_idf*tf_idf
                try:
                    doc_sums[doc] = (doc_sums[doc][0] + tf_idf, doc_sums[doc][1] + sqrs)
                except KeyError:
                    for i in prev_idf_sqrs:
                        sqrs += i
                    doc_sums[doc] = (tf_idf, sqrs)
            prev_idf_sqrs.append(idf*idf)
        except KeyError:
            continue
    for i, sums in doc_sums.items():
        doc_scores.append((i, sums[0]/math.pow(sums[1], .5)))
    doc_scores = sorted(doc_scores, key=lambda tup: tup[1], reverse=True)
    return doc_scores
