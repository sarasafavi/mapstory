import textile

from django.conf import settings
from django.db import models


class Leader(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()

    def html(self):
        return textile.textile(self.content)