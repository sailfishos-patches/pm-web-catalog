from django import template


register = template.Library()


@register.filter(name='truncatelines')
def ellipses(value, count):
    return '\n'.join(value.split('\n')[:count] + [' ... more'])
