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
1. Social auth.
 * follow django-allauth.readthedocs.io/en/latest/installation.html instruction
 * edit python3.6/site-packages/allauth/socialaccount/fields.py as described here: https://github.com/python-social-auth/social-app-django/pull/102/files
 * change domain name in /admin -> Sites to `localhost:8000` (`mundep.com:8000`)
 * add social applications in /admin -> Social applications using keys and tokens provided
 * only enter site as http://localhost:8000 (`mundep.com:8000`) (127.0.0.1 won't work with fb authenification)
 * VK has smth with profile links. Edit 8th line in python3.6/site-packages/allauth/socialaccount/providers/vk/provider.py: `return self.account.extra_data.get('link') or "https://vk.com/id{}".format(self.account.extra_data.get('uid'))`

2. To run locally without using containers, specify the following environment variables:
 * DKRD_DB_NAME
 * DKRD_DB_USER
 * DKRD_DB_PASSWORD
 * DKRD_DB_HOST
 * DKRD_DB_PORT

 * DKRD_SITE_DOMAIN
 * DKRD_SITE_PREFIX
 * DKRD_ALLOWED_HOSTS
 * DKRD_SECRET_KEY
 * DKRD_DEBUG

or check that defaults in app/cain/settings.py suffice.

3. To run in containers, simply use `docker-compose -f docker-compose.MODE.yml up` in root dir — this launches project in required mode.
 * local — accepts mundep.lc, builds from ., DEBUG = True
 * test — for CI tests in Travis
 * dev — accepts mundep.dv, builds from repo with :dev tag, DEBUG = True
 * prestable — accepts mundep.ps, builds from repo with :master tag, DEBUG = True
 * stable — accepts mundep.com, builds from repo with :master tag, DEBUG = False
If it's first run for db, before starting run `docker-compose -f docker-compose.MODE.yml run web bash -c 'python3 app/manage.py migrate; python3 app/manage.py fill_db; python3 app/manage.py collectstatic --noinput'`