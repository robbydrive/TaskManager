from django.shortcuts import render, render_to_response
from .forms import CreateTask
from datetime import datetime


def index(request):
    response = render_to_response('index.html', {})
    return response


def task_form(request):
    field1 = field2 = field_err = ''
    sign = 0
    if request.method == 'POST':
        form = CreateTask(request.POST)
        info = 'Форма заполнена, но некорректна'
        field_err = form.errors
        if form.is_valid():
            info = 'Форма заполнена и корректна'
            field1 = form.cleaned_data['title']
            field2 = form.cleaned_data['estimate']
            delta = str(field2 - datetime.date(datetime.now()))
            delta = '0' if delta.find('day') == -1 else delta.split()[0]
            if int(delta) <= 3:
                sign = 1
    else:
        info = 'Форма не заполнена'
        form = CreateTask()
    return render(
        request, 'task_form.html',
        {'form': form, 'info': info, 'field1': field1, 'field2': field2, 'sign': sign, 'err': field_err}
    )