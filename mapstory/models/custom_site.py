from django.db import models
from django.contrib.sites.models import Site


class CustomSite(models.Model):
    site = models.OneToOneField(Site, null=True, related_name='assets')
    subtitle = models.CharField(max_length=100)
    logo = models.ImageField(blank=False, upload_to='customsite')
    favicon = models.ImageField(blank=False, upload_to='customsite')
    footer_text = models.TextField()

    class Meta:
        verbose_name = "Custom Site Property"
        verbose_name_plural = "Custom Site Properties"

    def __unicode__(self):
        return 'Properties of {0}'.format(self.site.domain)

    def save(self, *args, **kwargs):
        super(CustomSite, self).save(*args, **kwargs)
        # Cached information will likely be incorrect now.
        Site.objects.clear_cache()