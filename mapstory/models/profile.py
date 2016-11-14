from django.db import models
from django.contrib.auth.models import Group

from geonode.people.models import Profile
from geonode.people.models import profile_post_save


def mapstory_profile_post_save(instance, sender, **kwargs):
    profile_post_save(instance, sender, **kwargs)
    registered_group, created = Group.objects.get_or_create(name='registered')
    instance.groups.add(registered_group)
    Profile.objects.filter(id=instance.id).update()

models.signals.post_save.connect(mapstory_profile_post_save, sender=Profile)
