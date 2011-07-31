# -*- coding: utf-8 -*-
from optparse import make_option
import shutil
import re
from django.db import connections
import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from settings import ROOT_PATH
import lxml.html
from lxml import etree
from pyquery import PyQuery as pq
from livedocs.models import Item, ItemAnchor
from livedocs.models import Version
from settings import STATIC_ROOT
from settings import STATIC_URL


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
                    default='1.3',
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
        if not 'ver' in options or not options['ver']:
            raise CommandError('Enter version')

        try:
            self.version = Version.objects.get(name=options['ver'])
        except Version.DoesNotExist:
            self.version = None

        if options['delete']:
            if self.version:
                self.delete_version()
            else:
                raise CommandError('You are deleting non-existent version')
        else:
            if self.version:
                self.delete_version()
            else:
                self.version = Version(name=options['ver'], is_default=options['default'])
                self.version.save()

            if not options['only_parse']:
                self._download_docs()
                self._make_html()
            self._parse_html_and_update_db()


    def delete_version(self):
        print 'Deleting version {0} ...'.format(self.version.name)
        try:
            Item.objects.filter(version=self.version)[0].get_root().delete()
        except IndexError:
            pass


    def _download_docs(self):
        """ Download latest docs from svn repository """
        print 'Downloading {0} docs...'.format(self.version.name)

        args = ['rm', '-rf', os.path.join(ROOT_PATH, self.LOCAL_PATH, '*')]
        subprocess.call(args)
        svn_url = self.SVN_TRUNK if self.version.name == 'dev' else self.SVN_TAG.format(self.version.name)
        args = ['svn', 'co', os.path.join(svn_url, self.PATH_TO_DOCS), self.LOCAL_PATH]
        subprocess.call(args)


    def _make_html(self):
        """ Process RST with Sphinx documentor as signle file """
        print 'Print processing RST...'

        args = ['make', 'singlehtml']
        subprocess.call(args, cwd = os.path.join(ROOT_PATH, self.LOCAL_PATH))


    def _parse_html_and_update_db(self):
        print 'Parsing HTML...'

        file = open(os.path.join(ROOT_PATH, self.LOCAL_PATH, '_build/singlehtml/contents.html'))
        document = lxml.html.document_fromstring(file.read())
        document = self.import_images(document)
        content = document.get_element_by_id('contents')

        print 'Updating db...'

        self.parse_section(content)
        self.create_paths()
        self.replace_links()


    def parse_section(self, parent_element, parent_section=None, additional_anchors=[]):
        """ Parsing section """

        parent_element_classes = parent_element.attrib.get('class', '').split(' ')

        # Construct Item
        section = Item(version=self.version)
        section.content = ''
        if hasattr(parent_element, 'is_root'):
            section.is_root = parent_element.is_root
        if parent_section:
            parent_ancestors = [parent_section] + list(parent_section.get_ancestors(ascending=True))
            for item in parent_ancestors:
                if item.is_root:
                    section.parent = item
                    break
            if not section.parent:
                section.parent = parent_section

        subitems = []
        anchors = [] + additional_anchors
        section_elements_anchors = []

        # Iterating over child nodes
        for children_element in parent_element:

            # Do we have any subsections?
            children_element_classes = set(children_element.attrib.get('class', '').split(' '))
            
            if self.SUB_ITEMS_CLASSES & children_element_classes:

                if 'compound' in parent_element_classes:
                    children_element.is_root = True
                subitems.append(children_element)
                section_elements_anchors.append(children_element.attrib.get('id', None))

            else:

                # Filling section
                if children_element.tag in self.HEADER_TAGS:
                    section.title = children_element.text_content().encode('utf8')
                elif children_element.tag == 'span' and not children_element.text_content():
                    anchors.append(children_element.attrib['id'])
                else:
                    section.content += lxml.html.tostring(children_element)

        self.prepare_section(section)
        is_section_empty = not section.title

        # Save Item if it isn't empty
        if not is_section_empty or not parent_section:
            if anchors:
                section.slug = self.get_slug(anchors)
            section.save()

            # Save anchors
            for anchor in anchors:
                ItemAnchor(name=anchor, item=section).save()

        # Save subitems
        for i, item in enumerate(subitems):
            if is_section_empty:
                if parent_section:
                    parent_for_item = parent_section
                else:
                    parent_for_item = section
            else:
                parent_for_item = section

            # Pick up anchors for subitem
            subsection_additional_anchors = []
            if section_elements_anchors[i]:
                subsection_additional_anchors.append(section_elements_anchors[i])
            if is_section_empty and len(subitems) == len(anchors):
                subsection_additional_anchors.append(anchors[i])

            self.parse_section(item, parent_for_item,
                               additional_anchors=subsection_additional_anchors)


    def get_slug(self, anchors):
        # Get good anchor for slug
        if len(anchors) > 1:
            anchors_without_ids = [a for a in anchors if not re.match(r'id\d+', a)]
            if anchors_without_ids:
                for a in anchors_without_ids:
                    if not '-' in a:
                        return a

        return anchors[0]

    
    def prepare_section(self, section):
        section.title = section.title.replace('¶', '')
        section.content = section.content.replace('\n</pre>', '</pre>')


    def import_images(self, document):
        """Copy images to static root and fix img src"""
        SRC = os.path.join(ROOT_PATH, self.LOCAL_PATH, '_build/singlehtml/_images')
        DST = os.path.join(STATIC_ROOT)
        args = ['cp', SRC, DST, '-R']
        subprocess.call(args)

        for element, attribute, link, pos in document.iterlinks():
            if attribute == "src":
                 new_src = os.path.join(STATIC_URL,link)
                 element.set('src', new_src)
        return document


    def create_paths(self):
        """Filling site paths at once"""
        print 'Filling paths ...'

        for section in Item.objects.all():
            ancestors = section.get_ancestors()
            section.path = '/'.join([a.slug for a in ancestors][2:] + [section.slug])
            section.save()


    def replace_links(self):
        """ Replace links concern many anchors """
        print 'Replacing links ...'

        def replacer(match):
            original_link = match.groups()[0]
            link_parts = original_link.split('#')
            link = link_parts[1] if len(link_parts) > 1 else link_parts[0]

            anchors = ItemAnchor.objects.filter(name=link, item__version=self.version)
            if anchors:
                new_link = anchors[0].item.get_absolute_url()
                return 'href="{0}"'.format(new_link)
            else:
                items = Item.objects.filter(content__contains='id="{0}"'.format(link),
                                            version=self.version)
                if items:
                    new_link = '{0}#{1}'.format(items[0].get_absolute_url(), link)
                    return 'href="{0}"'.format(new_link)
                else:
                    if 'http://' in original_link:
                        return 'href="{0}"'.format(original_link)
                    else:
                        return ''

        for section in Item.objects.all():
            section.content = re.sub(r'href="(.+)"', replacer, section.content)
            section.save()




