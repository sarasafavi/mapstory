from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from .AdminClient import AdminClient

from datetime import datetime
from geonode.contrib.collections.models import Collection
from geonode.groups.models import GroupProfile


def test_organizations(self):
    admin = AdminClient()
    admin.login_as_admin()
    response = admin.get(reverse('organization_create'))
    self.assertEqual(response.status_code, 200)
    self.assertHasGoogleAnalytics(response)

    # Create new organization
    form_data = {'social_twitter': 'notreal', 'social_facebook': 'notreal', 'title': 'Test Organization',
                 'description': 'Testing', 'email': 'test@test.com', 'access': 'public', 'date_joined': datetime.now(),
                 'city': 'Victoria', 'country': 'CAN', 'keywords': 'test', 'profile_type': 'org', 'slug': 'Test-Organization'}
    response = admin.post(reverse('organization_create'), data=form_data)
    # Redirect when form is submitted, therefore 302
    self.assertEqual(response.status_code, 302)

    # When the organization is created, a GroupProfile and Collection model pointing to it should be created
    group = GroupProfile.objects.all().first()
    collection = Collection.objects.all().first()
    self.assertEqual(collection.group, group)

    # Test editing the organization
    form_data = {'title': 'Test Organization', 'description': 'Edit', 'keywords': 'edit', 'profile_type': 'org',
                 'access': 'public', 'slug': 'Test-Organization', 'date_joined': datetime.now()}
    response = admin.post(reverse('organization_edit', args=[group.slug]), data=form_data)
    # Redirect when form is submitted, therefore 302
    self.assertEqual(response.status_code, 302)

    group = GroupProfile.objects.all().first()
    self.assertEqual(group.description, 'Edit')
    group_keywords = []
    for keyword in group.keywords.all():
        group_keywords.append(keyword.name)
    self.assertEqual(group_keywords, ['edit'])

    # Make sure the detail page can be viewed by a regular user
    c = Client()
    response = c.get(reverse('organization_detail', args=[group.slug]))
    self.assertEqual(response.status_code, 200)