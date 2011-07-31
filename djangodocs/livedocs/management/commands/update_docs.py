# -*- coding: utf-8 -*-
from optparse import make_option
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
                raise CommandError('You are delete non exists version')
        else:
            if self.version:
                self.delete_version()
            else:
                self.version = Version(name=options['ver'], is_default=options['default'])
                self.version.save()

#            if not options['only_parse']:
#                self._download_docs()
#                self._make_html()
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
        self.replace_links()


    def parse_section(self, parent_element, parent_section=None, additional_anchors=[]):
        """ Parsing section """

        section = Item(version=self.version)
        section.content = ''
        if parent_section:
            section.parent = parent_section

        subitems = []
        anchors = [] + additional_anchors
        section_elements_anchors = []

        # Iterating over child nodes
        for children_element in parent_element:

            # Do we have any subsections?
            children_element_classes = set(children_element.attrib.get('class', '').split(' '))
            
            if self.SUB_ITEMS_CLASSES & children_element_classes:

                subitems.append(children_element)
                section_elements_anchors.append(children_element.attrib.get('id', None))

            else:

                # Filling section
                if children_element.tag in self.HEADER_TAGS:
                    title_content = children_element.text_content().encode('utf8')
                    section.title = title_content.replace('¶', '')
                elif children_element.tag == 'span' and not children_element.text_content():
                    anchors.append(children_element.attrib['id'])
                else:
                    section.content += lxml.html.tostring(children_element)

        is_section_empty = not section.title

        # Save Item if it isn't empty
        if not is_section_empty or not parent_section:
            if anchors:
                anchors.sort(key=lambda a: len(a))
                section.slug = anchors[0]
            section.save()

            # save anchors
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


    def import_images(self):
        """Copy images to static root"""
        SRC = os.path.join(ROOT_PATH, 'data/_build/singlehtml/_images')
        DST = os.path.join(STATIC_ROOT, '_images')
        shutil.copytree(SRC, DST)


    def create_paths(self):
        """Filling site paths at once"""
        print 'Filling paths ...'

        for section in Item.objects.all():
            ancestors = section.get_ancestors()
            section.path = '/'.join([a.slug for a in ancestors][2:] + [section.slug])
            section.save()


    def replace_links(self):
        """ Replace links concern many anchors """
        print 'Replace links ...'

        count = [0, 0]

        def replacer(match):
            link = match.groups()[0].strip('#')
            anchors = ItemAnchor.objects.filter(name=link, item__version=self.version)
            if anchors:
                count[0] += 1
                new_link = anchors[0].item.get_absolute_url()
                return 'href="{0}"'.format(new_link)
            else:
                count[1] += 1
                return ''

        for section in Item.objects.all():
            section.content = re.sub(r'href="([#\w\.]+)"', replacer, section.content)
            section.save()

        print count




