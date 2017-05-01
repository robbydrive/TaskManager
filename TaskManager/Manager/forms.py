from datetime import date
import re
from Manager import models
from django.forms import ModelForm, widgets
from django.core.exceptions import ValidationError


class TaskCreateForm(ModelForm):

    # title = fields.CharField(
    #     label='Заголовок: ',
    #     required=True, max_length=30,
    # )
    #
    # estimate = fields.DateField(
    #     label='Cрок выполнения: ',
    #     required=True,
    #     widget=widgets.SelectDateWidget()
    # )

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

    class Meta:
        model = models.Task
        fields = ['title', 'estimate', 'roadmap']
        widgets = {
            'estimate': widgets.SelectDateWidget(),
        }


class TaskEditForm(ModelForm):

    # title = fields.CharField(
    #     label='Заголовок: ',
    #     required=True, max_length=30,
    # )
    #
    # estimate = fields.DateField(
    #     label='Cрок выполнения: ',
    #     required=True,
    #     widget=widgets.SelectDateWidget()
    # )
    #
    # state = fields.ChoiceField(
    #     label='Состояние: ',
    #     required=True,
    #     choices=models.CHOICES
    # )

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
        if value is None or value not in (models.IN_PROGRESS, models.READY):
            raise ValidationError('Wrong state', code="wrong state")
        return value

    class Meta:
        model = models.Task
        fields = ['title', 'estimate', 'state']
        widgets = {
            'estimate': widgets.SelectDateWidget(),
        }
