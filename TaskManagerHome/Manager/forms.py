from datetime import date
import re
from Manager import models
from django.forms import ModelForm, widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
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


class CustomUserEditForm(ModelForm):

    class Meta:
        model = models.User
        fields = ['email', 'phone', 'first_name', 'last_name', 'age', 'region',]


class CustomUserEditCutForm(ModelForm):

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'age', 'region']


class CustomPasswordChangeForm(PasswordChangeForm):

    error_messages = dict(PasswordChangeForm.error_messages, **{
        'same_passwords': "You entered two same passwords. Change the new password or abort the operation"
    })

    def clean_new_password1(self):
        if self.cleaned_data.get('old_password') == self.cleaned_data.get('new_password1'):
            raise ValidationError(
                self.error_messages['same_passwords'],
                code="same_passwords"
            )
        return self.cleaned_data.get('new_password1')
