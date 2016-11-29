# Organization forms
class OrganizationForm(GroupForm):

    class Meta:
        model = GroupProfile
        exclude = ['group', 'profile_type', 'tasks', 'featured']


class OrganizationUpdateForm(GroupUpdateForm):

    class Meta:
        model = GroupProfile
        exclude = ['group', 'profile_type', 'tasks', 'featured']