from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

from geonode.contrib.collections.models import Collection
from geonode.groups.models import GroupProfile

from mapstory.journal import get_group_journals

from forms import OrganizationForm, OrganizationUpdateForm


def organization_detail(request, slug):
    group = GroupProfile.objects.get(slug=slug)

    if not group.profile_type == 'org':
        return HttpResponse(status=404)

    return render_to_response("groups/organization_detail.html", {
        "id": group.id,
        "journals": get_group_journals(group),
        "managers": group.get_managers().all()
    }, context_instance=RequestContext(request))


@login_required
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.profile_type = 'org'
            group.save()
            form.save_m2m()
            group.join(request.user, role="manager")
            # Create the collection corresponding to this organization
            collection = Collection()
            collection.name = group.title
            collection.slug = group.slug
            collection.group = group
            collection.save()
            return HttpResponseRedirect(
                reverse(
                    "organization_detail",
                    args=[
                        group.slug]))
    else:
        form = OrganizationForm(initial={'profile_type': 'org'})

    if request.user.is_superuser:
        return render_to_response("groups/group_create.html", {
            "form": form,
        }, context_instance=RequestContext(request))
    else:
        return HttpResponse(status=403)


@login_required
def organization_edit(request, slug):
    group = GroupProfile.objects.get(slug=slug)
    if not group.profile_type == 'org':
        return HttpResponse(status=404)
    # Can use this function to toggle manager view
    if not group.user_is_role(request.user, role="manager"):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = OrganizationUpdateForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()
            return HttpResponseRedirect(
                reverse(
                    "organization_detail",
                    args=[
                        group.slug]))
    else:
        form = OrganizationForm(instance=group)

    return render_to_response("groups/group_update.html", {
        "form": form,
        "group": group,
    }, context_instance=RequestContext(request))


def organization_members(request, slug):
    group = get_object_or_404(GroupProfile, slug=slug)
    ctx = {}

    if not group.can_view(request.user):
        raise Http404()

    if group.access in [
        "public-invite",
        "private"] and group.user_is_role(
        request.user,
        "manager"):
        ctx["invite_form"] = GroupInviteForm()

    if group.user_is_role(request.user, "manager"):
        ctx["member_form"] = GroupMemberForm()

    ctx.update({
        "group": group,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
    })
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/organization_members.html", ctx)


@require_POST
@login_required
def organization_members_add(request, slug):
    group = get_object_or_404(GroupProfile, slug=slug)

    if not group.user_is_role(request.user, role="manager"):
        return HttpResponseForbidden()

    form = GroupMemberForm(request.POST)

    if form.is_valid():
        role = form.cleaned_data["role"]
        for user in form.cleaned_data["user_identifiers"]:
            group.join(user, role=role)

    return redirect("organization_detail", slug=group.slug)


@login_required
def organization_member_remove(request, slug, username):
    group = get_object_or_404(GroupProfile, slug=slug)
    user = get_object_or_404(get_user_model(), username=username)

    if not group.user_is_role(request.user, role="manager"):
        return HttpResponseForbidden()
    else:
        GroupMember.objects.get(group=group, user=user).delete()
        user.groups.remove(group.group)
        return redirect("organization_detail", slug=group.slug)


@require_POST
def organization_invite(request, slug):
    group = get_object_or_404(GroupProfile, slug=slug)

    if not group.can_invite(request.user):
        raise Http404()

    form = GroupInviteForm(request.POST)

    if form.is_valid():
        for user in form.cleaned_data["invite_user_identifiers"].split("\n"):
            group.invite(
                user,
                request.user,
                role=form.cleaned_data["invite_role"])

    return redirect("organization_members", slug=group.slug)
