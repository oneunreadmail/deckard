from django import template
import mistune

register = template.library()


@register.filter
def markdown(value):
    markdown = mistune.Markdown()
    return markdown(value)