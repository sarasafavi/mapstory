from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from mapstory.models.content_mixin import ContentMixin


class DiaryEntry(ContentMixin):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    show_on_main = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % (self.title)

    def get_absolute_url(self):
        return reverse('diary-detail', args=[self.pk])

    class Meta:
        verbose_name_plural = 'DiaryEntries'


def get_group_journals(gProfile):
    users = gProfile.group.user_set.all()
    journals = []
    for user in users:
        journals.append(DiaryEntry.objects.filter(author=user))

    return [item for sublist in journals for item in sublist]