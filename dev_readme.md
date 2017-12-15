1. How to drop all public tables in PosgreSQL:

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO djangoadmin; --Your Django user
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema'; -- (Not important)`
```
After that run makemigrations and migrate commands.


2. Template settings in settings.py to support both Django and jinja2 template engines
(store your jinja2 templates in deckard/templates/jinja2/deckard):

```TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'deckard/templates/jinja2'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'PROJECT_NAME.jinja2.environment'
        },
    }
]
```