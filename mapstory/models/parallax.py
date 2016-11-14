from django.db import models


class ParallaxImage(models.Model):
    name = models.CharField(max_length=64, blank=True)
    image = models.ImageField(upload_to='parallax', max_length=255)

    def __unicode__(self):
        return self.image.url


def get_images():
    return ParallaxImage.objects.all()