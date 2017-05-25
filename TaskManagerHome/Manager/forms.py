from datetime import date
import re
from Manager import models
from django.forms import ModelForm, widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError


class TaskCreateForm(ModelForm):

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value is None or not re.sub(r'\s', r'', value):
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
        if value is None or not re.sub(r'\s', r'', value):
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
        if value is None or not re.sub(r'\s', r'', value):
            raise ValidationError('Title can not be empty', code="Empty title")
        return value

    class Meta:
        model = models.Roadmap
        fields = ['title']


class CustomUserCreationForm(UserCreationForm):

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if not email or models.User.objects.filter(email=email).exists():
            raise ValidationError("Wrong email - probably it is already in use")
        return email

    def save(self, commit=True):
        self.instance.username = self.instance.email
        return super(CustomUserCreationForm, self).save(commit)

    class Meta:
        model = models.User
        fields = UserCreationForm.Meta.fields + ('email', 'phone', 'first_name', 'last_name', 'age', 'region',)
        exclude = ('username',)


class CustomAuthenticationForm(AuthenticationForm):

    class Meta:
        model = models.User
