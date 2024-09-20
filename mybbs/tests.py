from django.test import TestCase

# Create your tests here.

from django.db.models import Count
import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bbs.settings")
    import django

    django.setup()

    from mybbs import models


    # books = models.Article.objects.annotate(c=Count('tag'))
    # books = models.Article.objects.annotate(c=Count('tag')).values('title', 'c')
    # print(books)

    # class Aa:
    #     def __init__(self, name):
    #         self.name = name
    #
    #     def __str__(self):
    #         return self.name
    #
    #
    # obj = Aa('EGON')
    # print(obj, type(obj))
    # print(str(obj), type(str(obj)))
