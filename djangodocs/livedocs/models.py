from django.db import models
from django.db.models import permalink
from mptt.models import MPTTModel


class Version(models.Model):
    name = models.CharField('Version of docs', max_length=10)
    is_default = models.BooleanField('Display by default', default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Version'
        verbose_name_plural = 'Versions'


class Item(MPTTModel, models.Model):
    slug = models.SlugField('Slug', max_length=1000)
    path = models.CharField('Path in docs', max_length=1000)
    title = models.CharField('Title', max_length=1000)
    content = models.TextField('Content')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'Parent')
    version = models.ForeignKey(Version)

    def __unicode__(self):
        return self.slug

    @permalink
    def get_absolute_url(self):
        return ('item', (), {'item_path': self.path, 'current_version': self.version.name})

    def get_breadcrumbs(self):
        return self.get_ancestors().filter(level__gte=3)

    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Content'
