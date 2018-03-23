from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import re
from django import template
import mistune

register = template.Library()

CUT_PATTERNS = [
    r"{cut ([^\}]*)}",
]


@register.filter(name="markdown")
def markdown(value):
    md = mistune.Markdown()
    return md(value)


@register.filter(name="times")
def times(number):
    return range(int(number))


@register.filter(name="youtube")
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


def collapsed(text, link):
    for pattern in CUT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return text[:match.start()] + '<a href="{}">{}</a>'.format(link, match.group(1))
    return text


def expanded(text):
    for pattern in CUT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return text[:match.start()] + text[match.end():]
    return text


@register.filter(name="addcss")
def addcss(field, css):
    class_old = field.field.widget.attrs.get("class", None)
    class_new = class_old + ' ' + css if class_old else css
    return field.as_widget(attrs={"class": class_new})


@register.filter(name='urlencode')
def urlencode(uri, **query):
    parts = list(urlparse(uri))
    q = parse_qs(parts[4])
    q.update(query)
    parts[4] = urlencode(q)
    return urlunparse(parts)
