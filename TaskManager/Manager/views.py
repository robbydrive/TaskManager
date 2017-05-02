from datetime import datetime
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from Manager.forms import TaskCreateForm, TaskEditForm, RoadmapAddForm
from Manager.models import Task, Roadmap


def index(request):
    return render(request, 'index.html', {'existing_data': Task.objects.all()})


def tasks(request, roadmap_id=None):
    return render(request, 'tasks.html',
                  {'existing_data': Task.objects.all() if roadmap_id is None
                   else Task.objects.filter(roadmap=Roadmap.objects.get(pk=roadmap_id)),
                   'parent_roadmap': Roadmap.objects.get(pk=roadmap_id) if roadmap_id is not None
                   else None})


def add_task(request, roadmap_id=None):
    is_critical = 0
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            is_critical = 1 if int(delta) <= 3 else 0
            form.state = 'in_progress'
            form.save()
    else:
        form = TaskCreateForm()
        form.fields['roadmap'].initial = roadmap_id
    return render(
        request, 'task_add_form.html',
        {'form': form, 'isCritical': is_critical, 'roadmap_id': roadmap_id}
    )


def edit_task(request, task_id):
    is_critical = 0
    task_to_edit = Task.objects.get(pk=task_id)
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task_to_edit)
        if form.is_valid():
            delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            is_critical = 1 if int(delta) <= 3 else 0
            form.save()
    else:
        form = TaskEditForm(instance=task_to_edit)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'isCritical': is_critical,
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