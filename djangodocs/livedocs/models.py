from django.db import models
from mptt.models import MPTTModel

class Version(models.Model):
    name = models.CharField('Version of docs', max_length=10)
    is_default = models.BooleanField('Display by default', default=False)

    class Meta:
        verbose_name = 'Version'
        verbose_name_plural = 'Versions'


class Item(MPTTModel):
    title = models.CharField('Title', max_length=100)
    content = models.TextField('Content')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'Parent')
    version = models.ForeignKey(Version)

    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Content'