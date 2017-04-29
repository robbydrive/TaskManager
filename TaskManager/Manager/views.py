from datetime import datetime
import json
from django.shortcuts import render
from Manager.forms import TaskCreateForm, TaskEditForm
from Manager.models import Task, Roadmap


def index(request):
    return render(request, 'index.html', {'existing_data': Task.objects.all()})


def add_task(request):
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
    return render(
        request, 'task_add_form.html',
        {'form': form, 'isCritical': is_critical}
    )


def edit_task(request, task_id):
    is_critical = 0
    if request.method == 'POST':
        form = TaskEditForm(request.POST)
        if form.is_valid():
            delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            is_critical = 1 if int(delta) <= 3 else 0
            form.save()
    else:
        task_to_edit = Task.objects.get(pk=task_id)
        form = TaskEditForm(task_to_edit)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'isCritical': is_critical,
                                                   'task_id': task_id})
