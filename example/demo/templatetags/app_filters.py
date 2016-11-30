from django import template


register = template.Library()


@register.filter(name='truncatelines')
def truncatelines(value, count):
    lines = value.split('\n')
    result = '\n'.join(lines[:count])
    if len(lines) > count:
        result += '\n ... more'
    return result
