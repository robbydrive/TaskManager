from django.forms import Form, fields, widgets
from django.core.exceptions import ValidationError
from datetime import date


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
        if value == "" or value is None:
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value is None or value < date.today():
            raise ValidationError('Date is in the past', code="Past date")
        return value
