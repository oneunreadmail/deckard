# this adds {{ test }} to every context so it can be used in a template


def custom_context(request):
    return {'test': 'custom context works'}
