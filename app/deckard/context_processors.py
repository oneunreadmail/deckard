# this adds {{ test }} to every context so it can be used in a template
from cain.settings import SITE_DOMAIN, SITE_PREFIX


def custom_context(request):
    return {
        'domain': SITE_DOMAIN,
        'prefix': SITE_PREFIX,
    }
