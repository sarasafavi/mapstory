from django.db import models

from mapstory.models.content_mixin import ContentMixin


class NewsItem(ContentMixin):
    title = models.CharField(max_length=64)

    @property
    def publication_time(self):
        return self.date
