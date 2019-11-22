from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .utils import *
from .query_handler import query

def home(request):
    context = {}
    return render(request, 'home/home.html', context)


def index(request):
    return HttpResponse('Index HERE')


def results(request):
    result_dict = {}
    term_string = request.GET['query']
    if term_string == '#episodes':
        return episodes(request)
    elif term_string == '#characters':
        return ponies(request)

    terms = term_string.split()
    # query expansion, and pre processing here stored to terms

    # ranked query results here stored to doc_list
    doc_list = sorted(query(term_string), key=lambda x: x[1])
    print(doc_list)
    # doc_list = sorted(list(Document.objects.all()), key=lambda x: x.id)
    for i in doc_list:
        result_dict[Document.objects.filter(id=i[0])[0].title] = get_lines_keywords(terms, i[0])[0:5]

    if len(result_dict) == 0:
        results_header = "Sorry, no results for " + term_string + " or there is a problem with the query"
    else:
        results_header = ""
    context = {'results_header': results_header,
               'terms_list': terms,
               'result_dict': result_dict,
               'term_string': term_string,
               }
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
    #create_new_chars()
    #create_char_episode()
    #create_episode_files("ponyportal\static\All_transcripts.txt", "ponyportal\static\episodes\\")
    return HttpResponse("running some function....")