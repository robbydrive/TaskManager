from datetime import date
import re
from Manager import models
from django.forms import ModelForm, widgets, ModelChoiceField
from django.core.exceptions import ValidationError


class TaskCreateForm(ModelForm):

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
        fields = ['title', 'estimate', 'state', 'roadmap']
        widgets = {
            'estimate': widgets.SelectDateWidget(),
        }


class RoadmapAddForm(ModelForm):

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value is None or len(re.sub(r'\s', r'', value)) == 0:
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    class Meta:
        model = models.Roadmap
        fields = ['title']