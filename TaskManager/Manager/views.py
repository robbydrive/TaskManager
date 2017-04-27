from django.shortcuts import render, render_to_response
from Manager.forms import CreateTask, EditTask
from datetime import datetime
import json


def getExistingData():
    existingData = []
    try:
        fp = open("tmp.json", "r")
        existingData = json.load(fp)
        fp.close()
    except OSError:
        pass
    return existingData


def index(request):
    response = render_to_response('index.html', {'existing_data': getExistingData()})
    return response


def add_task(request):
    isCritical = 0
    if request.method == 'POST':
        form = CreateTask(request.POST)
        if form.is_valid():
            delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            isCritical = 1 if int(delta) <= 3 else 0
            existingData = getExistingData()
            with open("tmp.json", "w") as fp:
                existingData.append({'title': form.cleaned_data['title'],
                                     'estimate': str(form.cleaned_data['estimate']),
                                     'state': 'in_progress'})
                json.dump(existingData, fp)
    else:
        form = CreateTask()
    return render(
        request, 'task_add_form.html',
        {'form': form, 'isCritical': isCritical}
    )


def edit_task(request, task_title):
    existingData = getExistingData()
    isCritical = 0
    if request.method == 'POST':
        form = EditTask(request.POST)
        if form.is_valid():
            with open("tmp.json", "w") as fp:
                for object in existingData:
                    title = object.get('title', None)
                    if title is not None and title == task_title:
                        delta = str(form.cleaned_data['estimate'] - datetime.date(datetime.now()))
                        delta = '0' if delta.find('day') == -1 else delta.split()[0]
                        isCritical = 1 if int(delta) <= 3 else 0
                        object['title'] = form.cleaned_data['title']
                        object['estimate'] = str(form.cleaned_data['estimate'])
                        object['state'] = form.cleaned_data['state']
                        break
                json.dump(existingData, fp)
    else:
        data = dict()
        for object in existingData:
            title = object.get('title', None)
            if title is not None and title == task_title:
                data = object
                data['estimate'] = datetime.strptime(data['estimate'], '%Y-%m-%d')
                break
        form = EditTask(data)
    return render(request, 'task_edit_form.html', {'form': form,
                                                   'isCritical': isCritical,
                                                   'task_title': task_title })


