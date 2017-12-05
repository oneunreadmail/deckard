from django import template
import mistune

register = template.Library()


@register.filter(name="markdown")
def markdown(value):
    md = mistune.Markdown()
    return md(value)
