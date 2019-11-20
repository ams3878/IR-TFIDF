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
    terms = request.GET['query'].split()
    context = {'list': terms}
    return render(request, 'home/results.html', context)


def ponies(request):
    #create_new_chars()
    #create_char_episode()
    chars = sorted(list(Character.objects.all()), key=lambda x: x.id)
    context = {'list': chars,
               }
    return render(request, 'home/list.html', context)


def episodes(request):
    #create_episode_files("ponyportal\static\All_transcripts.txt", "ponyportal\static\episodes\\")
    episodes = sorted(list(Document.objects.all()), key=lambda x: x.id)
    context = {'list': episodes,
               }
    return render(request, 'home/list.html', context)
