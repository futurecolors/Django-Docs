# -*- coding: utf-8 -*-
from optparse import make_option
import shutil
import os
import subprocess
from django.core.management.base import BaseCommand
from settings import ROOT_PATH
import lxml.html
from livedocs.models import Item
from livedocs.models import Version
from settings import STATIC_ROOT


class Command(BaseCommand):
    help = 'Update livedocs database'
    SVN_TRUNK = 'http://code.djangoproject.com/svn/django/trunk/'
    SVN_TAG = 'http://code.djangoproject.com/svn/django/tags/releases/{0}/'
    PATH_TO_DOCS = 'docs'
    LOCAL_PATH = 'livedocs/data'
    HEADER_TAGS = ['h{0}'.format(i + 1) for i in range(10)]
    SUB_ITEMS_CLASSES = set(['toctree-wrapper', 'section'])

    option_list = BaseCommand.option_list + (
        make_option('--ver',
                    action='store',
                    dest='ver',
                    default=None,
                    help='Documentation version'),
        make_option('--delete',
                    action='store_true',
                    dest='delete',
                    default=False,
                    help='Delete version'),
        make_option('--default',
                    action='store_true',
                    dest='default',
                    default=False,
                    help='Is default version'),
        make_option('--only-parse',
                    action='store_true',
                    dest='only_parse',
                    default=False,
                    help='Do not download docs and dont launch sphinx'),
        )
    version = None

    def handle(self, *args, **options):
        self.import_images()
#        if not 'ver' in options or not options['ver']:
#            raise CommandError('Enter version')
#
#        try:
#            self.version = Version.objects.get(name=options['ver'])
#        except Version.DoesNotExist:
#            self.version = None
#
#        if options['delete']:
#            if self.version:
#                self.delete_version()
#            else:
#                raise CommandError('You are delete non exists version')
#        else:
#            if self.version:
#                self.delete_version()
#            else:
#                self.version = Version(name=options['ver'], is_default=options['default'])
#                self.version.save()
#
#            if not options['only_parse']:
#                self._download_docs()
#                self._make_html()
#
#        with transaction.commit_on_success():
#            self._parse_html_and_update_db()
#            self.create_paths()

    def delete_version(self):
        print 'Deleting version {0} ...'.format(self.version.name)
        try:
            Item.objects.filter(version=self.version)[0].get_root().delete()
        except IndexError:
            pass

    def _download_docs(self):
        """ Download latest docs from svn repository """
        print 'Downloading {0} docs...'.format(self.version.name)
        svn_url = self.SVN_TRUNK if self.version.name == 'dev' else self.SVN_TAG.format(self.version.name)
        args = ['svn', 'co', os.path.join(svn_url, self.PATH_TO_DOCS), self.LOCAL_PATH]
        subprocess.call(args)

    def _make_html(self):
        """ Process RST with Sphinx documentor as signle file """
        print 'Print processing RST...'
        args = ['make', 'singlehtml']
        subprocess.call(args, cwd = self.LOCAL_PATH)

    def _parse_html_and_update_db(self):
        print 'Parsing HTML...'

        file = open(os.path.join(ROOT_PATH, self.LOCAL_PATH, '_build/singlehtml/contents.html'))
        document = lxml.html.document_fromstring(file.read())
        content = document.get_element_by_id('contents')

        print 'Updating db...'
        self.parse_section(content)
        self.create_paths()


    def parse_section(self, parent_element, parent_section=None):
        """ Parsing section"""
            
        section = Item(version=self.version)
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
#                if 'toctree-wrapper' in children_element_classes:
#                    self.parse_section(children_element, parent_section)
#                else:
                self.parse_section(children_element, section)

            else:
                
                # Filling section
                if children_element.tag in self.HEADER_TAGS:
                    section.title = children_element.text or ''
                elif children_element.tag == 'span' and not children_element.text:
                    section.slug = children_element.attrib['id']
                else:
                    section.content += lxml.html.tostring(children_element)
                    
        section.save()


    def import_images(self):
        """Copy images to static root"""
        SRC = os.path.join(ROOT_PATH, 'data/_build/singlehtml/_images')
        DST = os.path.join(STATIC_ROOT, '_images')
        shutil.copytree(SRC, DST)

    def create_paths(self):
        """Filling site paths at once"""
        for section in Item.objects.all():
            ancestors = section.get_ancestors()
            section.path = '/'.join([a.slug for a in ancestors][2:] + [section.slug])
            section.save()




