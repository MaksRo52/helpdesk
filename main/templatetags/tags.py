from django import template

register = template.Library()


@register.filter()
def mymedia(path):
    if path:
        return f"../media/{path}"
    return "#"
