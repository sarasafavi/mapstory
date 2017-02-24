# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Max

from tastypie.test import ResourceTestCase, TestApiClient

from .models import Favorite
from geonode.base.models import TopicCategory
from geonode.base.populate_test_data import create_models
from geonode.documents.models import Document


class FavoriteTest(ResourceTestCase):
    """
    Tests mapstory.apps.favorite app/module
    """
    def setUp(self):

        # these are needed for the geonode fixtures
        TopicCategory.objects.create(identifier='biota')
        TopicCategory.objects.create(identifier='location')
        TopicCategory.objects.create(identifier='elevation')

        super(FavoriteTest, self).setUp()
        self.adm_un = "admin"
        self.adm_pw = "admin"
        create_models(type="document")
        self.list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'favorites'})
        self.api_client = TestApiClient()

    # tests of Favorite and FavoriteManager methods.
    def test_favorite(self):
        # grab a user and two docs from those created during setUp()
        test_user = get_user_model().objects.get(username="AnonymousUser")
        test_document_1 = Document.objects.get(title="lorem ipsum")
        test_document_2 = Document.objects.get(title="ipsum lorem")

        # test create favorite.
        Favorite.objects.create_favorite(test_document_1, test_user)
        Favorite.objects.create_favorite(test_document_2, test_user)
        favorites = Favorite.objects.all()
        self.assertEqual(favorites.count(), 2)
        ct = ContentType.objects.get_for_model(test_document_1)
        self.assertEqual(favorites[0].content_type, ct)

        # test all favorites for specific user.
        favorites_for_user = Favorite.objects.favorites_for_user(test_user)
        self.assertEqual(favorites_for_user.count(), 2)

        # test document favorites for user.
        document_favorites = Favorite.objects.favorite_documents_for_user(test_user)
        self.assertEqual(document_favorites.count(), 2)

        # test layer favorites for user.
        layer_favorites = Favorite.objects.favorite_layers_for_user(test_user)
        self.assertEqual(layer_favorites.count(), 0)

        # test map favorites for user.
        map_favorites = Favorite.objects.favorite_maps_for_user(test_user)
        self.assertEqual(map_favorites.count(), 0)

        # test user favorites for user.
        user_favorites = Favorite.objects.favorite_users_for_user(test_user)
        self.assertEqual(user_favorites.count(), 0)

        # test favorite for user and a specific content object.
        user_content_favorite = Favorite.objects.favorite_for_user_and_content_object(test_user, test_document_1)
        self.assertEqual(user_content_favorite.object_id, test_document_1.id)

        # test bulk favorites.
        bulk_favorites = Favorite.objects.bulk_favorite_objects(test_user)
        self.assertEqual(len(bulk_favorites[ct.name]), 2)
        self.assertEqual(len(bulk_favorites["layer"]), 0)
        self.assertEqual(len(bulk_favorites["map"]), 0)
        self.assertEqual(len(bulk_favorites["user"]), 0)

    # tests of view methods.
    def test_create_favorite_view(self):
        """
        call create view with valid user and content.
        then call again to check for idempotent.
        """
        self.client.login(username=self.adm_un, password=self.adm_pw)
        response = self._get_response("add_favorite_document", ("1",))

        # check persisted.
        favorites = Favorite.objects.all()
        self.assertEqual(favorites.count(), 1)
        ct = ContentType.objects.get_for_model(Document)
        self.assertEqual(favorites[0].content_type, ct)

        # check response.
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        self.assertEqual(json_content["has_favorite"], "true")
        expected_delete_url = reverse("delete_favorite", args=[favorites[0].pk])
        self.assertEqual(json_content["delete_url"], expected_delete_url)

        # call method again, check for idempotent.
        response2 = self._get_response("add_favorite_document", ("1",))

        # check still one only persisted, same as before second call.
        favorites2 = Favorite.objects.all()
        self.assertEqual(favorites2.count(), 1)
        self.assertEqual(favorites2[0].content_type, ct)

        # check second response.
        self.assertEqual(response2.status_code, 200)
        json_content2 = json.loads(response2.content)
        self.assertEqual(json_content2["has_favorite"], "true")
        self.assertEqual(json_content2["delete_url"], expected_delete_url)

    def test_create_favorite_view_login_required(self):
        """
        call create view, not logged in.
        expect a redirect to login page.
        """
        response = self._get_response("add_favorite_document", ("1",))
        self.assertEqual(response.status_code, 302)

    def test_create_favorite_view_id_not_found(self):
        """
        call create view with object id that does not exist.
        expect not found.
        """
        # get a pk that is not in the db for Document object.
        max_document_pk = Document.objects.aggregate(Max("pk"))
        pk_not_in_db = str(max_document_pk["pk__max"] + 1)

        self.client.login(username=self.adm_un, password=self.adm_pw)
        response = self._get_response("add_favorite_document", (pk_not_in_db,))
        self.assertEqual(response.status_code, 404)

    def test_delete_favorite_view(self):
        """
        call delete view with valid user and favorite id.
        then call again to check for idempotent.
        """
        self.client.login(username=self.adm_un, password=self.adm_pw)

        # grab the PK of an existing document
        valid_pk = Document.objects.get(title='lorem ipsum').id

        # first, add one to delete.
        response = self._get_response("add_favorite_document", (valid_pk,))

        # check persisted.
        favorites = Favorite.objects.all()
        self.assertEqual(favorites.count(), 1)
        ct = ContentType.objects.get_for_model(Document)
        self.assertEqual(favorites[0].content_type, ct)
        favorite_pk = favorites[0].pk

        # call delete method.
        response = self._get_response("delete_favorite", (favorite_pk,))

        # check no longer persisted.
        favorites = Favorite.objects.all()
        self.assertEqual(favorites.count(), 0)

        # check response.
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        self.assertEqual(json_content["has_favorite"], "false")

        # call method again, check for idempotent.
        response2 = self._get_response("delete_favorite", (favorite_pk,))

        # check still none persisted, same as before second call.
        favorites2 = Favorite.objects.all()
        self.assertEqual(favorites2.count(), 0)

        # check second response.
        self.assertEqual(response2.status_code, 200)
        json_content2 = json.loads(response2.content)
        self.assertEqual(json_content2["has_favorite"], "false")

    def test_delete_favorite_view_login_required(self):
        """
        call delete view, not logged in.
        expect a redirect to login page.
        """
        response = self._get_response("delete_favorite", ("1",))
        self.assertEqual(response.status_code, 302)

    def test_api_filtering(self):
        """Test api filtering and searching"""

        test_user = get_user_model().objects.get(username=self.adm_un)
        test_document_1 = Document.objects.get(id=1)
        test_document_2 = Document.objects.get(id=2)
        test_document_3 = Document.objects.get(id=3)
        # test create favorite.
        Favorite.objects.create_favorite(test_document_1, test_user)
        Favorite.objects.create_favorite(test_document_2, test_user)
        Favorite.objects.create_favorite(test_document_3, test_user)
        Favorite.objects.create_favorite(test_user, test_user)

        self.api_client.client.login(username=self.adm_un, password=self.adm_pw)
        #Keywords filtering
        filters = '?keyword=doctagunique'
        resp = self.api_client.get(self.list_url + filters)
        self.assertValidJSONResponse(resp)
        self.assertEquals(len(self.deserialize(resp)['objects']), 1)

        #Title filtering
        filters = '?title=lorem1'
        resp = self.api_client.get(self.list_url + filters)
        self.assertValidJSONResponse(resp)
        self.assertEquals(len(self.deserialize(resp)['objects']), 1)

        #Type filtering
        filters = '?type=profile'
        resp = self.api_client.get(self.list_url + filters)
        self.assertValidJSONResponse(resp)
        self.assertEquals(len(self.deserialize(resp)['objects']), 1)

        filters = '?type=document'
        resp = self.api_client.get(self.list_url + filters)
        self.assertValidJSONResponse(resp)
        self.assertEquals(len(self.deserialize(resp)['objects']), 3)

    def _get_response(self, input_url, input_args):
        return self.client.post(
            reverse(
                input_url,
                args=input_args
            ),
            content_type="application/json"
        )
