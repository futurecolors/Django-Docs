## About

Django Docs (http://djangodocs.com) — fancy django documentation with live search.

Our favorite framework Django has excellent documentation (https://docs.djangoproject.com/),
but some aspects of it are not perfect, basically it concerns searching. If you want to find something,
it's easier to use Google. The main purpose of Django Docs is to provide user-friendly searching
on the Django documentation.

How are we going to achieve this goal:

* give an answer, not a set of results;
* do not hide the search results;
* improve formatting for a better reading of documentation;
* live search, suggesting search results in process of typing.
* search suggestions (in the nearest future).

The first version of the project is being developed in the Django Dash 2011 contest. We have only 48 hours
to resolve this ambitious task. If you find any bugs or you have any idea how to make djangodocs.com better,
please write us in https://github.com/futurecolors/Django-Docs/issues. You can also send Pull Requests,
we will be happy to add improvements suggested by the community.

By the way, we have already made useful jQuery cheatsheet: http://futurecolors.ru/jquery/

## Install guide (you may do this in virtualenv)

1. ```git clone git://github.com/futurecolors/Django-Docs.git```
2. ```cd Django-Docs```
3. ```pip install -r pip_requirements.txt```
4. ```cd djangodocs/```
5. Change in settings.py DB settings.
6. ```python manage.py syncdb```
7. ```python manage.py migrate```
8. For generate livedocs DB (it will download and parse documentation from django svn):
```
python manage.py update_docs --ver=1.3 --default
```
9. Install Sphinx search server (for Debian):
```
apt-get install sphinxsearch
```
9. Create config for Sphinx (copy output to /etc/sphinx/sphinx.conf):
```
python manage.py generate_sphinx_config livedocs
```
10. Start Sphinx (for Debian):
```
/etc/init.d/sphinxsearch start
```
11. Create indexes:
```
indexer --all --rotate
```
10. ```python manage.py runserver``` and go to http://127.0.0.1:8000