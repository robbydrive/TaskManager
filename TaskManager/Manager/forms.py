from datetime import date
import re
from django.forms import Form, fields, widgets
from django.core.exceptions import ValidationError


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
        if value is None or len(re.sub(r'\s', r'', value)) == 0:
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

    IN_PROGRESS = 'in_progress'
    READY = 'ready'
    CHOICES = (
        (IN_PROGRESS, 'In progress',),
        (READY, 'Ready',)
    )

    state = fields.ChoiceField(
        label='Состояние: ',
        required=True,
        choices=CHOICES
    )

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value is None or len(re.sub(r'\s', r'', value)) == 0:
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value is None or value < date.today():
            raise ValidationError('Date is in the past', code="Past date")
        return value

    def clean_state(self):
        value = self.cleaned_data.get('state')
        if value is None or value not in (self.IN_PROGRESS, self.READY):
            raise ValidationError('Wrong state', code="wrong state")
        return value
