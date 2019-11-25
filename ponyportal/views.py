from django.shortcuts import render
from django.http import HttpResponse
from .custom_lib.query_expansion import expand_term
from .custom_lib.retrieval_algorithms import query
from .custom_lib.utils import get_index, get_stems, get_lines_keywords, get_pos_index, get_bigrams
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

# positional index
POSITIONAL_INDEX_DICT = get_pos_index('mlp_positions.tsv')

# bigrams
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


def results(request):
    season_filter = []
    print(request.GET)

    for i in request.GET:
        if i.find("Season") != -1:
            s = int(i[7:])
            if s == 11:
                season_filter += [11, 12, 13, 14]
            else:
                season_filter.append(s)
    facets = [(e.name, e.id, "checked") if e.id in season_filter else (e.name, e.id, "")
              for e in list(Season.objects.all())]
    t1 = time.time_ns()
    result_dict = {}
    term_string = request.GET['query']
    if term_string == '#episodes':
        return episodes(request)
    elif term_string == '#characters':
        return ponies(request)

    terms = term_string
    highlight_terms = term_string.split()
    # Store dice scores found while error checking to use later when getting related queries
    dice_scores = {}
    if len(terms) > 1 or terms[0] not in INDEX_DOC_FREQ_DICT:
        terms = clean_terms(terms.split(), INDEX_DOC_FREQ_DICT, DOC_DICT, INDEX_WINDOW_FREQ_DICT, dice_scores)

    # This gets the terms to add to the end of the query for the 'searches related to ...'
    additional_query_terms = get_additional_query_terms(terms.split(), INDEX_WINDOW_FREQ_DICT, dice_scores)
    # query expansion, and pre processing here stored to terms
    terms = expand_term(terms, STEM_DICT)
    # ranked query results here stored to doc_list
    doc_list = query(terms, INDEX_DOC_FREQ_DICT, DOC_DICT, 'tfidf')
    doc_objects = []
    for x in doc_list:
        doc_objects.append(Document.objects.filter(id=int(x[0]))[0])
    if len(season_filter) > 0:
        season_objects = [e for e in Season.objects.all() if (e.name, e.id, "checked") in facets]
        doc_objects = [e.episode for e in SeasonToDocument.objects.filter(season__in=[y for y in season_objects],
                                                                          episode__in=[x for x in doc_objects])]

    t2 = time.time_ns()
    for i in doc_objects[0:20]:
        result_dict[i.title] = (i.id, get_lines_keywords(highlight_terms, i.id))
    t3 = time.time_ns()
    if len(result_dict) == 0:
        results_header = "Sorry, no results for " + term_string + " or there is a problem with the query"
    else:
        results_header = ""
    context = {'results_header': results_header,
               'terms_list': terms,
               'result_dict': result_dict,
               'term_string': term_string,
               'facets': facets[0:-3],
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


def info(request):
    context = {
               }
    return render(request, 'home/info.html', context)

def main(request):
    # create_new_chars()
    # create_char_episode()
    # create_episode_files("ponyportal\static\All_transcripts.txt", "ponyportal\static\episodes\\")
    # create_stems("mlp_index.tsv")
    # create_index_tsv_positions()
    # make_bigrams(POSITIONAL_INDEX_DICT, INDEX_DOC_FREQ_DICT, .1)
    return HttpResponse("running some function....")