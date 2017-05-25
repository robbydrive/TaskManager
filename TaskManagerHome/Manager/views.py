from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, get_user
from django.contrib.auth.decorators import login_required
from Manager.forms import *
from Manager.models import Task, Roadmap, READY, User


def index(request):
    return render(request, 'index.html', {'existing_data': Task.objects.all()})


def tasks(request, roadmap_id=None):
    return render(request, 'tasks.html',
                  {'existing_data': Task.objects.all() if roadmap_id is None
                                    else Task.objects.filter(roadmap=Roadmap.objects.get(pk=roadmap_id)),
                   'parent_roadmap': Roadmap.objects.get(pk=roadmap_id) if roadmap_id is not None
                                     else None})


def add_task(request, roadmap_id=None):
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            form.cleaned_data['state'] = 'in_progress'
            form.save()
    else:
        form = TaskCreateForm()
        form.fields['roadmap'].initial = roadmap_id
    return render(
        request, 'task_add_form.html',
        {'form': form, 'roadmap_id': roadmap_id}
    )


def edit_task(request, task_id):
    task_to_edit = Task.objects.get(pk=task_id)
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


def delete_task(request, task_id):
    Task.objects.get(pk=task_id).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def roadmaps(request):
    return render(request, 'roadmaps.html', {'roadmaps': Roadmap.objects.all()})


def add_roadmap(request):
    if request.method == 'POST':
        form = RoadmapAddForm(request.POST)
        if form.is_valid():
            new_roadmap = form.save()
            return HttpResponseRedirect(reverse('add_task', kwargs={'roadmap_id': new_roadmap.id}))
    else:
        form = RoadmapAddForm()
    return render(request, 'roadmap_add_form.html', {'form': form})


def delete_roadmap(request, roadmap_id):
    Roadmap.objects.get(pk=roadmap_id).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def get_hot_tasks(request):
    hot_tasks = [task for task in Task.objects.all() if task.is_critical]
    failed_tasks = [task for task in Task.objects.all() if task.is_failed]
    return render(request, 'hot_and_failed.html', {'hot_tasks': hot_tasks,
                                                   'failed_tasks': failed_tasks})


def stat(request, roadmap_id):
    created_and_finished = Roadmap.created_and_finished_stat(roadmap_id)
    points = Roadmap.points_stat(roadmap_id)
    return render(request, 'stat.html', {'table1_lines': created_and_finished,
                                         'table2_lines': points})


def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_up_page.html', {'form': form})


def sign_in(request):
    if request.method == "POST":
        import ipdb
        ipdb.set_trace()
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('hot'))
    else:
        form = CustomAuthenticationForm()
    return render(request, 'sign_in_page.html', {'form': form})


def log_out(request):
    if request.method("POST"):
        logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required()
def profile(request):
    values = User.objects.values().get(pk=get_user(request).id)
    custom_fields = ('email', 'phone', 'first_name', 'last_name', 'age', 'region',)
    values = {key: values[key] for key in values.keys() if key in custom_fields}
    return render(request, 'show_profile.html', {'values': values})


@login_required()
def edit_profile(request):
    user = get_user(request)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'profile_edit_form.html', {'form': form})
