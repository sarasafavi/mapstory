import os

from django.db import models

from geonode.maps.models import Map

from mapstory.models.content_mixin import ContentMixin


class GetPage(models.Model):
    name = models.SlugField(max_length=32, unique=True,
                            help_text='Do NOT include the "get" prefix')
    title = models.CharField(max_length=32)
    subtitle = models.CharField(max_length=32, blank=True)

    def published_entries(self):
        return self.contents.filter(publish=True)

    def __unicode__(self):
        return 'GetPage: %s' % self.name


class GetPageContent(ContentMixin):
    title = models.CharField(max_length=64)
    subtitle = models.CharField(max_length=64, blank=True)
    example_map = models.ForeignKey(Map, null=True, blank=True)
    main_link = models.URLField(blank=False)
    external_link = models.URLField(blank=True)
    external_link_title = models.CharField(max_length=64, blank=True, null=True)
    page = models.ForeignKey(GetPage, related_name='contents')
    order = models.IntegerField(blank=True, default=0)
    video = models.FileField(upload_to='getpage', blank=True)
    video_embed_link = models.URLField(blank=True)

    def extension(self):
        if self.video.name is None:
            return 'mp4'
        name, extension = os.path.splitext(self.video.name)
        return extension[1:]

    class Meta:
        ordering = ['order']