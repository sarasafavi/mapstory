from django.conf.urls import patterns, url

from views import organization_create, organization_edit, organization_detail, organization_members
from views import organization_invite, organization_members_add, organization_member_remove

urlpatterns = patterns('journal.views',
                       url(r'^create/$', organization_create, name='organization_create'),
                       url(r'^(?P<slug>[^/]*)$', organization_detail, name='organization_detail'),
                       url(r'^edit/(?P<slug>[^/]*)$', organization_edit, name='organization_edit'),
                       url(r'^members/(?P<slug>[^/]*)$', organization_members, name='organization_members'),
                       url(r'^invite/(?P<slug>[^/]*)$', organization_invite, name='organization_invite'),
                       url(r'^(?P<slug>[^/]*)/members_add/$', organization_members_add, name='organization_members_add'),
                       url(r'^(?P<slug>[^/]*)/member_remove/(?P<username>.+)$', organization_member_remove, name='organization_member_remove'),
                       )
