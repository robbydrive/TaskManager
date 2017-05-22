from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Max, Min, F, ExpressionWrapper, DateTimeField
from Manager.forms import TaskCreateForm, TaskEditForm, RoadmapAddForm
from Manager.models import Task, Roadmap, READY


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
            form.state = 'in_progress'
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
        if form.is_valid():
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
    queryset = Task.objects.filter(roadmap=roadmap_id)
    created_dates = queryset.aggregate(min_date=Min('created'), max_date=Max('created'))
    min_date = created_dates['min_date']
    min_date = datetime.strptime(f'{min_date.year}-{min_date.isocalendar()[1]}-1', '%Y-%W-%w')
    finished_date = queryset.aggregate(max_date=Max('finished'))
    max_date = max(finished_date['max_date'], created_dates['max_date'])
    created_and_finished = []
    current = min_date.date()
    while current <= max_date:
        created_and_finished.append({
            'year': current.year,
            'weekno': current.isocalendar()[1],
            'start_date': current.strftime("%Y-%m-%d"),
            'end_date': (current + timedelta(days=6)).strftime("%Y-%m-%d"),
            'created_count': queryset.filter(created__range=[current, current + timedelta(days=6)]) \
                                     .count(),
            'finished_count': queryset.filter(state=READY,
                                              finished__range=[current, current + timedelta(days=6)]) \
                                      .count()
        })
        current += timedelta(weeks=1)
        print(current)
    return render(request, 'stat.html', {'min_date': min_date,
                                         'max_date': max_date,
                                         'table_lines': created_and_finished})
