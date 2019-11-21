from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .utils import *


def home(request):
    context = {}
    return render(request, 'home/home.html', context)


def index(request):
    return HttpResponse('Index HERE')


def results(request):
    result_dict = {}
    terms = []

    # query expansion, and pre processing here stored to terms
    terms_temp = request.GET['query'].split()
    for i in terms_temp:
        terms.append(i.lower())
    # ranked query results here stored to doc_list
    doc_list = sorted(list(Document.objects.all()), key=lambda x: x.id)
    for i in doc_list:
        line_matches = get_lines_keywords(terms, i.id)[0:5]
        if len(line_matches) != 0:
            result_dict[i] = line_matches
        if len(result_dict.keys()) == 5:
            break

    context = {'results_header': "Results for query...",
               'terms_list': terms,
               'result_dict': result_dict,
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