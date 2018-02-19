from django.contrib.staticfiles.storage import staticfiles_storage
from .basic import reverse
from jinja2 import Environment
from deckard.templatetags import filters


def reverse_upgrade(x, *args, **kwargs):
    return reverse(x, args=args, kwargs=kwargs)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse_upgrade,
    })
    env.filters['youtube'] = filters.youtube
    env.filters['collapsed'] = filters.collapsed
    env.filters['expanded'] = filters.expanded
    env.filters['markdown'] = filters.markdown
    env.filters['addcss'] = filters.addcss
    return env
