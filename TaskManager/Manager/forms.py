from django.forms import Form, fields, widgets
from django.core.exceptions import ValidationError
from datetime import date
import re


class CreateTask(Form):

    title = fields.CharField(
        label='Заголовок: ',
        required=True, max_length=30,
    )

    estimate = fields.DateField(
        label='Cрок выполнения: ',
        required=True,
        widget=widgets.SelectDateWidget()
    )

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value is None or len(re.sub(r'[ \t]', r'', value)) == 0:
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value is None or value < date.today():
            raise ValidationError('Date is in the past', code="Past date")
        return value


class EditTask(Form):

    title = fields.CharField(
        label='Заголовок: ',
        required=True, max_length=30,
    )

    estimate = fields.DateField(
        label='Cрок выполнения: ',
        required=True,
        widget=widgets.SelectDateWidget()
    )

    state = fields.CharField(
        label='Состояние: ',
        required=True,
        # widget=widgets.Select(choices=('in_progress', 'ready'))
    )

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value is None or len(re.sub(r'[ \t]', r'', value)) == 0:
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value is None or value < date.today():
            raise ValidationError('Date is in the past', code="Past date")
        return value

    def clean_state(self):
        value = self.cleaned_data.get('state')
        if value is None or value not in ('in_progress', 'ready'):
            raise ValidationError('Wrong state', code="wrong state")
        return value