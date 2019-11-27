"""
The only function in here of any importance is the results()
    this is the __main__ of the app and handles the majority of the i/o bewteen the user and the algorithms

all other functions just handle GET/POSTs from the webserver and displaying html pages


views.py
@author Aaron Smith, Grant Larsen
11/26/2019
"""

from django.shortcuts import render
from django.http import HttpResponse
from .custom_lib.query_expansion import expand_term
from .custom_lib.query_suggestion import  clean_terms, get_additional_query_terms
from .custom_lib.retrieval_algorithms import query
from .custom_lib.utils import get_index, get_stems, get_lines_keywords,\
    get_pos_index, get_bigrams, get_window_index, get_docs_index
from .models import *
from .custom_lib.indexer import create_window_index_tsv, create_index_tsv, create_index_tsv_positions,\
    make_bigrams, create_stems
import time

# ---------------------------------
#
# tsv files exists create the index dictionary on startup
# otherwise create the tsv, then the dictionary
# ---------------------------------
try:
    INDEX_DOC_FREQ_DICT = get_index('mlp_index.tsv')
except FileNotFoundError:
    print('mpl_index.tsv not found creating...')
    create_index_tsv()
    INDEX_DOC_FREQ_DICT = get_index('mlp_index.tsv')

try:
    INDEX_WINDOW_FREQ_DICT = get_window_index()
except FileNotFoundError:
    print('mpl_window_index.tsv not found creating...')
    create_window_index_tsv()
    INDEX_WINDOW_FREQ_DICT = get_window_index()

try:
    DOC_DICT = get_docs_index()
except FileNotFoundError:
    # TODO add function for creating doc_names.tsv
    DOC_DICT = get_docs_index()

# Stems
try:
    STEM_DICT = get_stems('mlp_stems.tsv')
except FileNotFoundError:
    print('mlp_stems.tsv not found creating...')
    create_stems("mlp_index.tsv")
    STEM_DICT = get_stems('mlp_stems.tsv')

# positional index
try:
    POSITIONAL_INDEX_DICT = get_pos_index('mlp_positions.tsv')
except FileNotFoundError:
    print('mlp_positions.tsv not found creating...')
    create_index_tsv_positions()
    POSITIONAL_INDEX_DICT = get_pos_index('mlp_positions.tsv')

# bigrams
try:
    BIGRAMS_DICT = get_bigrams('mlp_bigrams.tsv')
except FileNotFoundError:
    print('mlp_bigrams.tsv not found creating...')
    make_bigrams(POSITIONAL_INDEX_DICT, INDEX_DOC_FREQ_DICT, .1)
    BIGRAMS_DICT = get_bigrams('mlp_bigrams.tsv')


def home(request):
    try:
        pre_query = request.GET['pre_query']
    except KeyError:
        pre_query = "None"
    try:
        suggestions = list(BIGRAMS_DICT[pre_query].keys())
    except KeyError:
        suggestions = "None"
    # turn off auto-complete until it actually works
    suggestions = "None"
    context = {"suggestions": suggestions,
               "pre_query": pre_query
               }
    return render(request, 'home/home.html', context)


def index(request):
    return HttpResponse('Index HERE')

# --------------------------------------------------------------------------------------------------------
# the __main__ of the retrieval process#
#
# --------------------------------------------------------------------------------------------------------

def results(request):
    season_filter = []
    results_header = ""
    # get any selected season filter from GET
    for i in request.GET:
        if i.find("Season") != -1:
            s = int(i[7:])
            if s == 11:
                season_filter += [11, 12, 13, 14]
            else:
                season_filter.append(s)
    # create the facets and weather or not they will be checked on page reload
    facets = [(e.name, e.id, "checked") if e.id in season_filter else (e.name, e.id, "")
              for e in list(Season.objects.all())]
    t1 = time.time_ns()
    result_dict = {}
    # the query given by the user from GET
    term_string = request.GET['query'].lower()
    # see if any special commands were given, and execute them
    if term_string[0] == '#':
        if term_string[1:8] == '#episodes':
            return episodes(request)
        elif term_string[1:9] == '#characters':
            return ponies(request)
        elif term_string[1:8] == 'episode':
            return render(request, 'episodes_html/' + term_string[8:] + '.html')

    # create a list form the query string
    terms = term_string.split()
    # Store dice scores found while error checking to use later when getting related queries
    dice_scores = {}
    # fix any spelling errors, and return a list of query terms that match ones in the index
    terms_clean = clean_terms(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, INDEX_WINDOW_FREQ_DICT, dice_scores)
    # create a header to explain if spelling correction was needed
    if terms != terms_clean:
        results_header = "No reasults found for [" + term_string
        term_string = ' '.join(terms_clean)
        results_header += "] searching [" + term_string + "] instead..."
    # set terms to the new corrected list
    terms = terms_clean
    # This gets the terms to add to the end of the query for the 'searches related to ...'
    related = get_additional_query_terms(terms, INDEX_WINDOW_FREQ_DICT, dice_scores)[0:5]
    # query expansion, and pre processing here stored to terms
    terms = expand_term(terms, STEM_DICT)
    # get ranked results from tfidf, and store the idfs to use in doc sum
    doc_list, idf_list = query(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, 'tfidf')
    # get ranked results from BM25
    doc_list_bm = query(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, 'bm')
    # --------------------------------------
    #  prints used for trec eval should remove
    print("rank\ttfidf\tbm25\n", "--------------------------------\n")
    for i in range(10):
        if len(doc_list) > i:
            idfdoc = doc_list[i]
        else:
            idfdoc = ""
        if len(doc_list_bm) > i:
            bmdoc = doc_list_bm[i]
        else:
            bmdoc = ""
        print(i, "\t", idfdoc, bmdoc)
    # --------------------------------------
    # store idf results as final
    doc_list_final = doc_list
    # add BM25 results to that list, ignoring duplicates
    for i in doc_list_bm:
        if i not in doc_list_final:
            doc_list_final.append(i)
    # sort the new list
    doc_list_final = sorted(doc_list_final, key=lambda z: z[1], reverse=True)

    # get Django doc objects for any season in the filters that match the retrieved list
    doc_objects = []
    for x in doc_list_final:
        doc_objects.append((Document.objects.filter(id=int(x[0]))[0], x[1]))
    if len(season_filter) > 0:
        season_objects = [e for e in Season.objects.all() if (e.name, e.id, "checked") in facets]
        doc_objects = [(e.episode, x[1]) for e in SeasonToDocument.objects.filter(
            season__in=[y for y in season_objects],
            episode__in=[x for x in doc_objects])]

    t2 = time.time_ns()
    # do document summarization on the top 10 results, and highlight the keyword matches
    for i in doc_objects[0:10]:
        result_dict[i[0].title] = (i[0].id, get_lines_keywords(terms, idf_list, i[0].id))
    t3 = time.time_ns()
    # if query errors could not be correct inform the user
    if len(result_dict) == 0:
        results_header = "Sorry, no results for " + term_string + " or there is a problem with the query"

    # dictionary to send render in the html
    context = {'results_header': results_header,
               'terms_list': terms,
               'result_dict': result_dict,
               'term_string': term_string,
               'facets': facets[0:-3],
               'related': related,
               }
    # some timeing stuff to make sure things dont take too long
    print("Time to retrive docs:", (t2 - t1)/1000000, 'ms')
    print("Time to bold keywords:", (t3 - t2)/1000000, 'ms')
    print("Time to Query:", (time.time_ns() - t1)/1000000, 'ms')

    return render(request, 'home/results.html', context)


def ponies(request):

    chars = sorted(list(Character.objects.all()), key=lambda x: x.id)
    context = {'list': chars,
               }
    return render(request, 'home/list.html', context)


def episodes(request):
    episodes = sorted(list(Document.objects.all()), key=lambda x: x.id)
    context = {'list': episodes,
               }
    return render(request, 'home/list.html', context)


def info(request):
    context = {
               }
    return render(request, 'home/info.html', context)
