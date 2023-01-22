from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter(name='cur')
def currency(value):
    return type(value)

@register.simple_tag(takes_context=True)
def lst(context, sep, *args):
    return mark_safe('%s (Итого '
                     '<strong>%s</strong>) %s' % (sep.join(args), len(args), context['parsed_content']))

@register.inclusion_tag('news_output/22.html')
def ulst(*args):
    return {'items': args}
