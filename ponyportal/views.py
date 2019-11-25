from django.shortcuts import render
from django.http import HttpResponse
from .custom_lib.query_expansion import expand_term
from .custom_lib.retrieval_algorithms import query
from .custom_lib.utils import get_index, get_window_index, get_docs_index, get_stems, get_lines_keywords, clean_terms, get_additional_query_terms
from .custom_lib.indexer import *
from .models import *
import time

# reverse index TSV
#   window size: document
#   values: word frequency
#   format: term doc:freq
INDEX_DOC_FREQ_DICT = get_index()
INDEX_WINDOW_FREQ_DICT = get_window_index()
DOC_DICT = get_docs_index()

# Stems
STEM_DICT = get_stems('mlp_stems.tsv')

def home(request):
    context = {}
    return render(request, 'home/home.html', context)


def index(request):
    return HttpResponse('Index HERE')


def results(request):
    t1 = time.time_ns()
    result_dict = {}
    term_string = request.GET['query']
    if term_string == '#episodes':
        return episodes(request)
    elif term_string == '#characters':
        return ponies(request)

    terms = term_string.split()
    # Store dice scores found while error checking to use later when getting related queries
    dice_scores = {}
    if len(terms) > 1 or terms[0] not in INDEX_DOC_FREQ_DICT:
        terms = clean_terms(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, INDEX_WINDOW_FREQ_DICT, dice_scores)

    # This gets the terms to add to the end of the query for the 'searches related to ...'
    additional_query_terms = get_additional_query_terms(terms, INDEX_WINDOW_FREQ_DICT, dice_scores)
    # query expansion, and pre processing here stored to terms
    terms = expand_term(terms, STEM_DICT)
    # ranked query results here stored to doc_list
    doc_list = query(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, 'tfidf')
    t2 = time.time_ns()
    for i in doc_list:
        result_dict[Document.objects.filter(id=i[0])[0].title] = get_lines_keywords(terms, i[0])
    t3 = time.time_ns()
    if len(result_dict) == 0:
        results_header = "Sorry, no results for " + term_string + " or there is a problem with the query"
    else:
        results_header = ""
    context = {'results_header': results_header,
               'terms_list': terms,
               'result_dict': result_dict,
               'term_string': term_string,
               }

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


def main(request):
    # create_new_chars()
    # create_char_episode()
    # create_episode_files("ponyportal\static\All_transcripts.txt", "ponyportal\static\episodes\\")
    create_stems("mlp_index.tsv")
    return HttpResponse("running some function....")