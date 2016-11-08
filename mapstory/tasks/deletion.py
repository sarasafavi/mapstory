from geonode.maps.models import MapStory


@task(name='geonode.tasks.deletion.delete_mapstory', queue='cleanup')
def delete_mapstory(object_id):
    """
    Deletes a mapstory and the associated maps and the associated map layers.
    """

    try:
        map_obj = MapStory.objects.get(id=object_id)
    except MapStory.DoesNotExist:
        return

    chapters = map_obj.chapters
    for chapter in chapters:
        chapter.layer_set.all().delete()
        chapter.delete()

    map_obj.delete()