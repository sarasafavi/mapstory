from django.core.urlresolvers import reverse

from geonode.base.models import ResourceBase


class MapStory(ResourceBase):

    def get_absolute_url(self):
        return reverse('mapstory.views.map_detail', None, [str(self.id)])

    @property
    def chapters(self):
        return self.chapter_list.order_by('chapter_index')

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.title = conf['title']
        self.abstract = conf['abstract']
        self.is_published = conf['is_published']
        if conf['category'] is not None:
            self.category = TopicCategory(conf['category'])

        if self.uuid is None or self.uuid == '':
            self.uuid = str(uuid.uuid1())

        removed_chapter_ids = conf['removed_chapters']
        if removed_chapter_ids is not None and len(removed_chapter_ids) > 0:
            for chapter_id in removed_chapter_ids:
                map_obj = Map.objects.get(id=chapter_id)
                self.chapter_list.remove(map_obj)

        self.save()

    def viewer_json(self, user):

        about = {
            'title': self.title,
            'abstract': self.abstract,
            'owner': self.owner.name_long,
            'username': self.owner.username
        }

        config = {
            'id': self.id,
            'about': about,
            'chapters': [chapter.viewer_json(user) for chapter in self.chapters],
            'thumbnail_url': '/static/geonode/img/missing_thumb.png'
        }

        return config

    def update_thumbnail(self, first_chapter_obj):
        if first_chapter_obj.chapter_index != 0:
            return

        chapter_base = ResourceBase.objects.get(id=first_chapter_obj.id)
        ResourceBase.objects.filter(id=self.id).update(
            thumbnail_url=chapter_base.thumbnail_url
        )

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'MapStories'
        db_table = 'maps_mapstory'
        pass

    @property
    def class_name(self):
        return self.__class__.__name__
