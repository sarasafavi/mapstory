from django.db import models
from django.template.defaultfilters import slugify

from geonode.people.models import Profile
from geonode.layers.models import Layer

from mapstory.models.diary import DiaryEntry
from mapstory.models.stamp import _stamp


class Community(models.Model):
    name = models.CharField(max_length=64, unique=True)
    icon = models.ImageField(blank=False, upload_to='communities')
    description = models.TextField(blank=True)
    order = models.IntegerField(blank=True, default=0)
    stamp = models.CharField(max_length=8, blank=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    layer = models.ManyToManyField(Layer, blank=True)
    leads = models.ManyToManyField(Profile, blank=True)
    journals = models.ManyToManyField(DiaryEntry, blank=True)

    def url(self):
        return self.icon.url + "?" + self.stamp

    def save(self, *args, **kwargs):
        if self.icon.name:
            self.stamp = _stamp(self.icon.read())
        super(Community, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Community - %s' % self.name

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'communities'

    def image_tag(self):
        return u'<img src="%s" />' % self.url()
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class Task(models.Model):
    task = models.TextField(blank=True)
    community = models.ForeignKey(Community, related_name='tasks')


def name_post_save(instance, *args, **kwargs):
    Community.objects.filter(name=instance.name).update(slug=(slugify(instance.name)))

models.signals.post_save.connect(name_post_save, sender=Community)
