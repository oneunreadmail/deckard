from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment
from deckard.templatetags.filters import youtube


def reverse_upgrade(x, *args, **kwargs):
    return reverse(x, args=args, kwargs=kwargs)


def environment(**options):
    env = Environment(extensions=['jinja2.ext.i18n'], **options)
    env.install_gettext_translations(translation, newstyle=False)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse_upgrade,
    })
    env.filters['youtube'] = youtube
    return env
