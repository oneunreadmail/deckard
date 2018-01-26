from django.urls import reverse as reverse_url
from cain.settings import SITE_DOMAIN, SITE_PREFIX


def reverse(x, args=(), kwargs={}):
    if "blog_name" in kwargs:
        blog_name = kwargs.pop("blog_name")
        return SITE_PREFIX + blog_name + "." + SITE_DOMAIN + reverse_url(x, args=args, kwargs=kwargs)
    else:
        return SITE_PREFIX + SITE_DOMAIN + reverse_url(x, args=args, kwargs=kwargs)
