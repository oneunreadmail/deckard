from urllib.parse import urlparse, parse_qs
import re
from django import template
import mistune

register = template.Library()


@register.filter(name="markdown")
def markdown(value):
    md = mistune.Markdown()
    return md(value)


@register.filter(name='times')
def times(number):
    return range(int(number))


@register.filter(name='youtube')
def youtube(text):
    embed = """<br/><center>
    <iframe width="560" height="315" 
    src="https://www.youtube.com/embed/{}" 
    frameborder="0" gesture="media" allow="encrypted-media" allowfullscreen></iframe>
    </center><br/>"""
    pattern = r'\S*youtube.com/\S*'

    def get_youtube_id(url):
        cgi_dict = parse_qs(urlparse(url).query)
        if "v" in cgi_dict:
            return cgi_dict["v"][0]
        else:
            raise Exception("Cannot parse non-youtube url")

    def replace_with_embed(match):
        url = match.group(0)
        return embed.format(get_youtube_id(url))

    return re.sub(pattern, replace_with_embed, text)
