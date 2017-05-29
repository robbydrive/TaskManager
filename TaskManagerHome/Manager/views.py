from django.shortcuts import render, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import login, logout, get_user, update_session_auth_hash
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.decorators import login_required
from Manager.forms import CustomPasswordChangeForm, CustomUserCreationForm, CustomAuthenticationForm, \
    TaskCreateForm, TaskEditForm, RoadmapAddForm, CustomUserEditForm, CustomUserEditCutForm
from Manager.models import Task, Roadmap, User
from social_django.models import UserSocialAuth


def index(request):
    user = get_user(request)
    if not isinstance(user, User):
        return render(request, 'index.html')
    return HttpResponseRedirect(reverse('hot'))


@login_required()
def tasks(request, roadmap_id=None):
    return render(request, 'tasks.html',
                  {'existing_data': Task.objects.filter(user=get_user(request)) if roadmap_id is None
                                    else Task.objects.filter(user=get_user(request),
                                                             roadmap=Roadmap.objects.get(pk=roadmap_id)),
                   'parent_roadmap': Roadmap.objects.filter(user=get_user(request)).get(pk=roadmap_id)
                                     if roadmap_id is not None else None})


@login_required()
def add_task(request, roadmap_id=None):
    user = get_user(request)
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        form.fields['roadmap'].queryset = Roadmap.objects.filter(user=user)
        if form.is_valid() and \
                ((form.instance.roadmap and form.instance.roadmap.user == user) or form.instance.roadmap is None):
            form.cleaned_data['state'] = 'in_progress'
            form.instance.user = user
            form.save()
            messages.success(request, "Task was created successfully")
        elif form.is_valid():
            form.add_error('roadmap', 'Roadmap does not belong to user from task')
    else:
        form = TaskCreateForm()
        form.fields['roadmap'].queryset = Roadmap.objects.filter(user=user)
        form.fields['roadmap'].initial = roadmap_id
    return render(
        request, 'task_add_form.html',
        {'form': form, 'roadmap_id': roadmap_id}
    )


@login_required()
def edit_task(request, task_id):
    user = get_user(request)
    try:
        task_to_edit = Task.objects.filter(user=user).get(pk=task_id)
    except Task.DoesNotExist:
        return Http404("Wrong task_id for edit task")
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task_to_edit)
        if form.is_valid() and form.cleaned_data['state'] == Task.READY and task_to_edit.roadmap.user == user:
            form.instance.ready()
            messages.success(request, "Task was edited successfully")
        elif form.is_valid() and task_to_edit.roadmap.user == user:
            form.save()
            messages.success(request, "Task was edited successfully")
        elif form.is_valid():
            form.add_error('roadmap', 'Roadmap does not belong to user from task')
    else:
        form = TaskEditForm(instance=task_to_edit)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'task_id': task_id})


@login_required()
def delete_task(request, task_id):
    Task.objects.filter(user=get_user(request)).get(pk=task_id).delete()
    messages.success(request, "Task was deleted successfully")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def roadmaps(request):
    return render(request, 'roadmaps.html', {'roadmaps': Roadmap.objects.filter(user=get_user(request))})


@login_required()
def add_roadmap(request):
    if request.method == 'POST':
        form = RoadmapAddForm(request.POST)
        if form.is_valid():
            form.instance.user = get_user(request)
            new_roadmap = form.save()
            messages.success(request, "New roadmap was created! Now let's create new task for it")
            return HttpResponseRedirect(reverse('add_task', kwargs={'roadmap_id': new_roadmap.id}))
    else:
        form = RoadmapAddForm()
    return render(request, 'roadmap_add_form.html', {'form': form})


@login_required()
def delete_roadmap(request, roadmap_id):
    try:
        Roadmap.objects.get(user=get_user(request), pk=roadmap_id).delete()
        messages.success(request, "Roadmap was deleted successfully")
    except Roadmap.DoesNotExist:
        return Http404("Wrong roadmap_id for delete_roadmap")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def get_hot_tasks(request):
    queryset = Task.objects.filter(user=get_user(request))
    hot_tasks = [task for task in queryset if task.is_critical]
    failed_tasks = [task for task in queryset if task.is_failed]
    return render(request, 'hot_and_failed.html', {'hot_tasks': hot_tasks,
                                                   'failed_tasks': failed_tasks})


@login_required()
def stat(request, roadmap_id):
    user = get_user(request)
    try:
        created_and_finished_stat = Roadmap.created_and_finished_stat(roadmap_id, user)
        points_months_stat = Roadmap.points_stat(roadmap_id, user)
    except ObjectDoesNotExist:
        return Http404("Probably wrong roadmap_id for stat")
    return render(request, 'stat.html', {'table1_lines': created_and_finished_stat,
                                         'table2_lines': points_months_stat})


def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New user was created successfully!")
            return HttpResponseRedirect(reverse('signin'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_up_page.html', {'form': form})


def sign_in(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "You logged in successfully")
            return HttpResponseRedirect(reverse('hot'))
    else:
        form = CustomAuthenticationForm()
    return render(request, 'sign_in_page.html', {'form': form})


def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required()
def profile(request):
    user = get_user(request)
    condition = user.social_auth.count() > 0
    r_messages = {message.extra_tags.split()[1]: message.message
                  for message in messages.get_messages(request)
                  if 'social-auth' in message.extra_tags}
    if condition:
        form = CustomUserEditCutForm(instance=user)
    else:
        form = CustomUserEditForm(instance=user)
    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
    return render(request, 'show_profile.html', {'form': form,
                                                 'github_login': github_login,
                                                 'can_disconnect': can_disconnect,
                                                 'r_messages': r_messages})


@login_required()
def edit_profile(request):
    user = get_user(request)
    if user.email == '':
        ProfileForm = CustomUserEditCutForm
    else:
        ProfileForm = CustomUserEditForm

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was edited successfully")
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = ProfileForm()
    return render(request, 'profile_edit_form.html', {'form': form})


@login_required()
def change_password(request):
    user = get_user(request)
    if user.has_usable_password():
        PasswordForm = CustomPasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == "POST":
        form = PasswordForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "You changed password successfully")
            return HttpResponseRedirect(reverse('hot'))
    else:
        form = PasswordForm(user)
    return render(request, 'password_change.html', {'form': form})
