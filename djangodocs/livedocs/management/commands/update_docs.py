# -*- coding: utf-8 -*-
from django.db import connections
import os
import subprocess
from django.core.management.base import BaseCommand
from settings import ROOT_PATH
import lxml.html
from lxml import etree
from pyquery import PyQuery as pq
from livedocs.models import Item


DISABLE_KEYS_SQL = 'SET FOREIGN_KEY_CHECKS = 0'
TRUNCATE_TABLE_SQL_PATTERN = 'TRUNCATE TABLE {0}'
ENABLE_KEYS_SQL = 'SET FOREIGN_KEY_CHECKS = 1'


def truncate_tables(tables):
    """ Очистка таблиц из списка """
    cursor = connections['default'].cursor()
    cursor.execute(DISABLE_KEYS_SQL)
    for table in tables:
        cursor.execute(TRUNCATE_TABLE_SQL_PATTERN.format(table))
    cursor.execute(ENABLE_KEYS_SQL)


class Command(BaseCommand):
    help = 'Update livedocs database'
    SVN_URL = 'http://code.djangoproject.com/svn/django/trunk/'
    PATH_TO_DOCS = 'docs'
    LOCAL_PATH = 'data'
    HEADER_TAGS = ['h{0}'.format(i + 1) for i in range(6)]
    SUB_ITEMS_CLASSES = set(['toctree-wrapper', 'section'])

    def handle(self, *args, **options):
#        self._download_docs(version='1.3')
#        self._make_html()
        self._parse_html_and_update_db()

    def _download_docs(self, version):
        """ Download latest docs from svn repository """
        print 'Downloading lastest docs...'
        args = ['svn', 'co', os.path.join(self.SVN_URL, self.PATH_TO_DOCS), self.LOCAL_PATH]
        subprocess.call(args)

    def _make_html(self):
        """ Process RST with Sphinx documentor as signle file """
        print 'Print processing RST...'
        args = ['make', 'singlehtml']
        subprocess.call(args, cwd = self.LOCAL_PATH)

    def _parse_html_and_update_db(self):
        print 'Parsing HTML...'

        file = open(os.path.join(ROOT_PATH, 'data/_build/singlehtml/contents.html'))
        document = lxml.html.document_fromstring(file.read())
        content = document.get_element_by_id('contents')

        print 'Updating db...'
        truncate_tables(['livedocs_item'])
        self.parse_section(content, 0)
        self.create_paths()


    def parse_section(self, parent_element, parent_section=None):
        """ Parsing section"""
        section = Item(version_id=1)
        section.content = ''
        if parent_section:
            section.parent = parent_section

        # Iterating over child nodes
        for children_element in parent_element:

            # Do we have any subsections?
            children_element_classes = set(children_element.attrib.get('class', '').split(' '))
            if self.SUB_ITEMS_CLASSES & children_element_classes:
                # Saving current section
                section.save()
                # Parsing child element
                self.parse_section(children_element, section)

            else:
                # Filling section
                if children_element.tag in self.HEADER_TAGS:
                    section.name = children_element.text
                elif  children_element.tag == 'span' and not children_element.text:
                    section.slug = children_element.attrib['id']
                else:
                    section.content += lxml.html.tostring(children_element)


    def create_paths(self):
        """Filling site paths at once"""
        for section in Item.objects.all():
            ancestors = section.get_ancestors()
            section.path = '/'.join([a.slug for a in ancestors][2:] + [section.slug])
            section.save()




