from django.shortcuts import render, HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import login, logout, get_user
from django.contrib.auth.decorators import login_required
from Manager.forms import CustomPasswordChangeForm, CustomUserCreationForm, CustomAuthenticationForm, \
    TaskCreateForm, TaskEditForm, RoadmapAddForm, CustomUserEditForm
from Manager.models import Task, Roadmap, User, READY
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
        if form.is_valid() and \
                ((roadmap_id and Roadmap.objects.get(pk=roadmap_id).user == user) or roadmap_id is None):
            form.cleaned_data['state'] = 'in_progress'
            form.instance.user = user
            form.save()
        elif form.is_valid():
            form.add_error('roadmap', 'Roadmap does not belong to user from task')
    else:
        form = TaskCreateForm()
        form.fields['roadmap'].initial = roadmap_id
    return render(
        request, 'task_add_form.html',
        {'form': form, 'roadmap_id': roadmap_id}
    )


@login_required()
def edit_task(request, task_id):
    try:
        task_to_edit = Task.objects.filter(user=get_user(request)).get(pk=task_id)
    except Task.DoesNotExist:
        return Http404("Wrong task_id for edit task")
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task_to_edit)
        if form.is_valid() and form.cleaned_data['state'] == READY:
            form.instance.ready()
        elif form.is_valid():
            form.save()
    else:
        form = TaskEditForm(instance=task_to_edit)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'task_id': task_id})

@login_required()
def delete_task(request, task_id):
    Task.objects.filter(user=get_user(request)).get(pk=task_id).delete()
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
            return HttpResponseRedirect(reverse('add_task', kwargs={'roadmap_id': new_roadmap.id}))
    else:
        form = RoadmapAddForm()
    return render(request, 'roadmap_add_form.html', {'form': form})


@login_required()
def delete_roadmap(request, roadmap_id):
    try:
        Roadmap.objects.get(user=get_user(request), pk=roadmap_id).delete()
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
        created_and_finished = Roadmap.created_and_finished_stat(roadmap_id, user)
        points = Roadmap.points_stat(roadmap_id, user)
    except ObjectDoesNotExist:
        return Http404("Probably wrong roadmap_id for stat")
    return render(request, 'stat.html', {'table1_lines': created_and_finished,
                                         'table2_lines': points})


def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('signin'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_up_page.html', {'form': form})


def sign_in(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
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

    # try:
    #     github_login = user.social_auth.get(provider='github')
    # except UserSocialAuth.DoesNotExist:
    #     github_login = None

    # can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
    form = CustomUserEditForm(instance=user)
    return render(request, 'show_profile.html', {'form': form})
                                                 # 'github_login': github_login,
                                                 # 'can_disconnect': can_disconnect})


@login_required()
def edit_profile(request):
    user = get_user(request)
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = CustomUserEditForm(instance=user)
    form.fields['email'].disabled = True
    return render(request, 'profile_edit_form.html', {'form': form})


@login_required()
def change_password(request):
    user = get_user(request)
    if request.method == "POST":
        form = CustomPasswordChangeForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('hot'))
    else:
        form = CustomPasswordChangeForm(user)
    return render(request, 'password_change.html', {'form': form})
