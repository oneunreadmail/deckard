**Database**
1. How to drop all public tables in PostgreSQL:

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO djangoadmin; -- Your Django user
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema'; -- (Not important)
```
After that run makemigrations and migrate commands.

2. Running tests in Django requires some DB privileges for Django user.
 In PostgreSQL run the following logged as postgres (superuser):
 
 ```alter user djangoadmin with createdb; -- Your Django user```


**Application**
1. local_settings.py example for development:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_db',
        'USER': 'djangoadmin',
        'PASSWORD': 'djangoadmin',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SECRET_KEY = 'some_secret_sequence_of_symbols'
ALLOWED_HOSTS = ["127.0.0.1", ".mundep.com"]
SESSION_COOKIE_DOMAIN = ".mundep.com"
DEBUG = True

STATICFILES_DIRS = [
]
```

2. Social auth.
 * follow django-allauth.readthedocs.io/en/latest/installation.html instruction
 * edit python3.6/site-packages/allauth/socialaccount/fields.py as described here: https://github.com/python-social-auth/social-app-django/pull/102/files
 * change domain name in /admin -> Sites to `localhost:8000` (`mundep.com:8000`)
 * add social applications in /admin -> Social applications using keys and tokens provided
 * only enter site as http://localhost:8000 (`mundep.com:8000`) (127.0.0.1 won't work with fb authenification)
 * VK has smth with profile links. Edit 8th line in python3.6/site-packages/allauth/socialaccount/providers/vk/provider.py: `return self.account.extra_data.get('link') or "https://vk.com/id{}".format(self.account.extra_data.get('uid'))`

3. To run in containers, simply use `docker-compose -f docker-compose.MODE.yml up` in root dir — this launchs project in required mode.
 * local — accepts mundep.lc, builds from ., DEBUG = True
 * test — for CI tests in Travis
 * dev — accepts mundep.dv, builds from repo with :dev tag, DEBUG = True
 * prestable — accepts mundep.ps, builds from repo with :master tag, DEBUG = True
 * stable — accepts mundep.com, builds from repo with :master tag, DEBUG = False
If it's first run for db, before starting run `docker-compose -f docker-compose.MODE.yml run web bash -c 'python3 app/manage.py migrate; python3 app/manage.py fill_db; python3 app/manage.py collectstatic --noinput'`