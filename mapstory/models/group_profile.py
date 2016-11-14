from geonode.groups.models import GroupProfile


def get_featured_groups():
    return GroupProfile.objects.filter(featured=True)