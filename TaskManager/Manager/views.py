from datetime import datetime
import json
from django.shortcuts import render, render_to_response
from Manager.forms import CreateTask, EditTask


def get_existing_data():
    existing_data = []
    try:
        fp = open("tmp.json", "r")
        existing_data = json.load(fp)
        fp.close()
    except OSError:
        pass
    return existing_data


def index(request):
    return render(request, 'index.html', {'existing_data': get_existing_data()})


def add_task(request):
    is_critical = 0
    if request.method == 'POST':
        form = CreateTask(request.POST)
        if form.is_valid():
            delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            is_critical = 1 if int(delta) <= 3 else 0
            existingData = get_existing_data()
            with open("tmp.json", "w") as fp:
                existingData.append({'title': form.cleaned_data['title'],
                                     'estimate': str(form.cleaned_data['estimate']),
                                     'state': 'in_progress'})
                json.dump(existingData, fp)
    else:
        form = CreateTask()
    return render(
        request, 'task_add_form.html',
        {'form': form, 'isCritical': is_critical}
    )


def edit_task(request, task_title):
    existing_data = get_existing_data()
    is_critical = 0
    if request.method == 'POST':
        form = EditTask(request.POST)
        if form.is_valid():
            with open("tmp.json", "w") as fp:
                for task_object in existing_data:
                    title = task_object.get('title', None)
                    if title is not None and title == task_title:
                        delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
                        delta = '0' if delta.find('day') == -1 else delta.split()[0]
                        is_critical = 1 if int(delta) <= 3 else 0
                        task_object['title'] = form.cleaned_data['title']
                        task_object['estimate'] = str(form.cleaned_data['estimate'])
                        task_object['state'] = form.cleaned_data['state']
                        break
                json.dump(existing_data, fp)
    else:
        data = dict()
        for task_object in existing_data:
            title = task_object.get('title', None)
            if title is not None and title == task_title:
                data = task_object
                data['estimate'] = datetime.strptime(data['estimate'], '%Y-%m-%d')
                break
        form = EditTask(data)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'isCritical': is_critical,
                                                   'task_title': task_title})
