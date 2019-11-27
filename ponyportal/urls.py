from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index, name='index'),
    path('ponies', views.ponies, name='ponies'),
    path('episodes', views.episodes, name='episodes'),
    path('results', views.results, name='results'),
    path('info', views.info, name='info'),
]
