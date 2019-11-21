from django.db import models
from django.core.files.storage import FileSystemStorage

docs = FileSystemStorage(location='static/episodes')
docs_tags = FileSystemStorage(location='static/episodes_tags')


class Character(models.Model):
    id = models.CharField(max_length=200, primary_key=True)


class Document(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    script_type = models.CharField(max_length=200)


class CharacterToDocument(models.Model):
    character = models.ForeignKey('Character', on_delete=models.DO_NOTHING)
    episode = models.ForeignKey('Document', on_delete=models.DO_NOTHING)


class Season(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)


class SeasonToDocument(models.Model):
    episode = models.ForeignKey('Document', on_delete=models.DO_NOTHING)
    season = models.ForeignKey('Season', on_delete=models.DO_NOTHING)
