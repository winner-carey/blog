# author:carey

from django import template
from mybbs import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag('cebianlan.html')
def cebianlan(user):
    blog = user.blog
    # 展示用户的标签以及每个标签对应的文章数
    tag_count = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c')

    # 展示分类
    category_count = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c')

    # 展示随笔档案
    year_article_list = models.Article.objects.filter(user=user).annotate(y_m=TruncMonth('create_date')).values(
        'y_m').annotate(
        c=Count('nid')).values_list(
        'y_m', 'c')

    return {
        'tag_count': tag_count,
        'category_count': category_count,
        'year_article_list': year_article_list,
        'username': user.username,

    }
