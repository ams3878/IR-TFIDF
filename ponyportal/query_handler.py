import math
import os
import time
import initialize

EPISODE_DIRECTORY = 'static/episodes_html/'
USE_TFIDF = True
MAX_DIST = 2
NUM_ASSOCIATIONS = 5
K_1 = 1.2
K_2 = 100.0
B = 0.75


def main():

    initialize.init()
    query('cutie mark crusaders')
    query('cutiemark crusader')
    query('best pony')


def query(query_string):

    start_time = time.perf_counter()
    terms = query_string.split()

    index = initialize.get_index()
    doc_index = initialize.get_doc_index()
    window_index = initialize.get_window_index()

    dice_scores = {}

    if len(terms) > 1 or terms[0] not in index:
        terms = clean_terms(terms, index, doc_index, window_index, dice_scores)
    if USE_TFIDF:
        results = query_tfidf(terms, index)
    else:
        results = query_bm25(terms, index, doc_index)

    associations = {}
    stop_words = get_stop_words()

    for term in terms:
        for similiar in find_associations(term, terms, window_index, stop_words, dice_scores):
            if similiar not in associations:
                associations[similiar[0]] = 0
            associations[similiar[0]] += similiar[1]

    similar_terms = []
    for term in associations:
        similar_terms.append((term, associations[term]))
    similar_terms = sorted(similar_terms, key=lambda tup: tup[1], reverse=True )
    print(time.perf_counter() - start_time, "seconds")

    response = {
        'results' : results,
        'query_changed' : ' '.join(terms) != query_string,
        'similar_terms' : similar_terms
    }
    print(response)
    return response


def clean_terms(terms, index, doc_index, window_index, dice_scores):
    fixed_terms = []

    if len(terms) == 1:
        adj_term = None
    else:
        adj_term = terms[1]
    for term in terms:
        if term != terms[0]:
            adj_term = fixed_terms[-1]
        most_similar = get_most_similar(term, adj_term, index, doc_index, window_index, dice_scores)
        if most_similar not in index and len(most_similar) > 1:
            for split in range(1, len(most_similar)):
                half1 = most_similar[:split]
                if half1 in index:
                    half2 = most_similar[split:]
                    if half2 in index:
                        fixed_terms.append(half1)
                        fixed_terms.append(half2)
                        break
        else:
            fixed_terms.append(most_similar)
    return fixed_terms

def get_most_similar(term, adj_term, index, doc_index, window_index, dice_scores):
    most_similar = term
    most_similar_score = 0
    doc_count = len(doc_index)
    for word in index:
        if abs(len(word) - len(term)) <= MAX_DIST:
            if term == word:
                dist = 0
            else:
                dist = get_levenshtein_distance(term, word)
            if dist <= 3:
                if dist == 0:
                    similarity = 1.5
                else:
                    similarity = 1 - dist / len(word)
                usage = int(index[word]['count']) / doc_count
                if adj_term in index:
                    dice = get_dice_coeff(window_index[adj_term], window_index[word])
                    if adj_term not in dice_scores:
                        dice_scores[adj_term] = {}
                    dice_scores[adj_term][word] = dice
                else:
                    dice = 0
                score = similarity * usage * dice
                if score > most_similar_score:
                    most_similar_score = score
                    most_similar = word

    return most_similar

def find_associations(word, terms, window_index, stop_words, dice_scores):
    associated_words = []
    min_coeff = 0
    indexed_word = window_index[word]
    if word in dice_scores:
        dice_index = dice_scores[word]
    else:
        dice_index = None
    for term in window_index:
        if term not in terms and term not in stop_words:
            compared_term = window_index[term]
            if dice_index is not None and term in dice_index:
                dice_coeff = dice_index[term]
            else:
                dice_coeff = get_dice_coeff(indexed_word, compared_term)
            if dice_coeff > min_coeff:
                if len(associated_words) < NUM_ASSOCIATIONS:
                    associated_words.append((term, dice_coeff))
                    if len(associated_words) == NUM_ASSOCIATIONS:
                        associated_words = sorted(associated_words, key=lambda tup: tup[1], reverse=True)
                else:
                    for ind in range(0, NUM_ASSOCIATIONS):
                        if dice_coeff > associated_words[ind][1]:
                            associated_words.insert(ind, (term, dice_coeff))
                            del associated_words[-1]
                            break
                min_coeff = associated_words[-1][1]
    return associated_words

def get_dice_coeff(term1, term2):
    term_intersects = 0
    for doc in term1:
        if doc != 'count' and doc in term2:
            intersect = [value for value in term1[doc] if value in term2[doc]]
            term_intersects += len(intersect)
    return 2*term_intersects/(term1['count'] + term2['count'])

def get_levenshtein_distance(term1, term2):
    matrix = [[0 for x in range(len(term2) + 1)] for x in range(len(term1) + 1)]

    for x in range(len(term1) + 1):
        matrix[x][0] = x
    for y in range(len(term2) + 1):
        matrix[0][y] = y

    for x in range(1, len(term1) + 1):
        for y in range(1, len(term2) + 1):
            if term1[x - 1] == term2[y - 1]:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1],
                    matrix[x][y - 1] + 1
                )
            else:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1] + 1,
                    matrix[x][y - 1] + 1
                )

    return matrix[len(term1)][len(term2)]

def query_bm25(terms, index, doc_index):
    term_counts ={}
    for term in terms:
        if term in term_counts:
            term_counts[term] += 1
        else:
            term_counts[term] = 1

    avg_dl = 0.0
    doc_scores = {}
    for doc in doc_index:
        avg_dl += float(doc_index[doc][1])

    avg_dl /= len(doc_index)
    n = len(doc_index)

    doc_k = {}
    for doc in doc_index:
        doc_k[doc] = K_1*((1 - B) + B * (float(doc_index[doc][1])/avg_dl))

    for term in term_counts:
        try:
            index_entry = index[term]
            n_i = float(index_entry['count'])
        except KeyError:
            continue

        term_weight = math.log(n/n_i, 10)

        query_term_weight = ((K_2 + 1)*term_counts[term])/(K_2 + term_counts[term])

        try:
            for doc, f_i in index[term]['docs'].items():
                k = doc_k[doc]
                doc_weight = (K_1 + 1)*f_i/(k + f_i)

                if doc not in doc_scores:
                    doc_scores[doc] = 0.0
                doc_scores[doc] += term_weight*doc_weight*query_term_weight

        except KeyError:
            continue
    doc_scores = [(doc, doc_scores[doc]) for doc in doc_scores]
    doc_scores = sorted(doc_scores, key=lambda tup: tup[1], reverse=True)
    return doc_scores

def query_tfidf(terms, index):
    num_docs = len([name for name in os.listdir(EPISODE_DIRECTORY) if os.path.isfile(os.path.join(EPISODE_DIRECTORY, name))]) * 1.0
    docs = {}
    for i in range(int(num_docs)):
        docs[i + 1] = ('None', 0)
    doc_sums = {}
    doc_scores = []
    for term in terms:
        idf = find_idf(term, index, num_docs)
        try:
            for doc, frequency in index[term]['docs'].items():
                tf = math.log(frequency + 1)
                tf_idf = tf * idf
                try:
                    doc_sums[doc] = (doc_sums[doc][0] + tf_idf, doc_sums[doc][1] + math.pow(tf_idf, 2))
                except KeyError:
                    doc_sums[doc] = (tf_idf, math.pow(tf_idf, 2))

        except KeyError:
            continue
    for i, sums in doc_sums.items():
        doc_scores.append((i, sums[0] / sums[1]))
    doc_scores = sorted(doc_scores, key=lambda tup: tup[1])
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

def get_stop_words():
    return ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out',
            'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into',
            'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the',
            'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were',
            'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to',
            'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have',
            'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can',
            'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself',
            'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by',
            'doing', 'it', 'how', 'further', 'was', 'here', 'than', 'get']

if __name__ == "__main__":
    main()