from django.db import models

class Version(models.Model):
    name = models.CharField(u'Version of docs', max_length=10)
    is_default = models.BooleanField(u'Display by default', default=False)

    class Meta:
        verbose_name = 'Version'
        verbose_name_plural = 'Versions'