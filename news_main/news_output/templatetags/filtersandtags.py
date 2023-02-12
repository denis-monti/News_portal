from django import template

register = template.Library()

@register.filter(name='index_for_comment_sub')
def index_for_comment_sub(indexable, i):
    if i == 0:
        return 0
    return indexable[i - 1]

@register.filter(name='index_for_count_like_dislike')
def index(indexable, i):
    return indexable[i]['total']

@register.filter(name='index_for_news')
def index(indexable, i):
    return indexable[i]['news']

@register.filter(name='get_item')
def get_item(Queryset):
    return Queryset.id



