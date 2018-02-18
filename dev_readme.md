1. How to drop all public tables in PostgreSQL:

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO djangoadmin; -- Your Django user
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema'; -- (Not important)
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

3. Media settings for development.  
Add to settings.py:
```
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Add to urls.py:
```
from . import settings
from django.contrib.staticfiles.urls import static
...
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

4. Running tests in Django requires some DB privileges for Django user.
 In PostgreSQL run the following logged as postgres (superuser):
 
 ```alter user djangoadmin with createdb; -- Your Django user```

5. Social auth.
 * follow django-allauth.readthedocs.io/en/latest/installation.html instruction
 * edit python3.6/site-packages/allauth/socialaccount/fields.py as described here: https://github.com/python-social-auth/social-app-django/pull/102/files
 * change domain name in /admin -> Sites to `localhost:8000`
 * add social applications in /admin -> Social applications using keys and tokens provided
 * only enter site as http://localhost:8000 (127.0.0.1 won't work with fb authenification)
 * VK has smth with profile links. Edit 8th line in python3.6/site-packages/allauth/socialaccount/providers/vk/provider.py: `return self.account.extra_data.get('link') or "https://vk.com/id{}".format(self.account.extra_data.get('uid'))`
 * should be it

6. Youtube embedding
 * In settings.py in TEMPLATES section replace `environment` to ```"environment": "deckard.jinja2.environment"```
 * Delete root jinja2.py, not needed anymore

7. Middleware and context processors
 * add ```'context_processors': [
                'deckard.context_processors.custom_context',
            ]``` to settings.py -> TEMPLATES -> OPTIONS (only for jinja2)
 * add ```'deckard.middleware.UserIsContributorMiddleware',``` to settings.py -> MIDDLEWARE

8. How to test subdomains locally:
 * add to local_settings.py:
    ```
    ALLOWED_HOSTS = ["127.0.0.1", ".mundep.com"]
    SESSION_COOKIE_DOMAIN = ".mundep.com"
    ```
 * add to hosts:
    ```
    127.0.0.1       mundep.com
    127.0.0.1       blogname.mundep.com
    ```
    for each blogname

9. To run in containers, simply use `docker-compose -f docker-compose.MODE.yml up` in root dir — this launchs project in required mode.
 * local — accepts mundep.lc, builds from ., DEBUG = True
 * test — for CI tests in Travis
 * dev — accepts mundep.dv, builds from repo with :dev tag, DEBUG = True
 * prestable — accepts mundep.ps, builds from repo with :master tag, DEBUG = True
 * stable — accepts mundep.com, builds from repo with :master tag, DEBUG = False
If it's first run for db, before starting run `docker-compose -f docker-compose.MODE.yml run web bash -c 'python3 app/manage.py migrate; python3 app/manage.py fill_db; python3 app/manage.py collectstatic --noinput'`