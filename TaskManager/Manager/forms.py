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

    def clean(self):
        cleaned_data = super().clean()
        value_title_clean = self.cleaned_data.get('title')
        value_date_clean = self.cleaned_data.get('estimate')
        if value_date_clean is not None and value_date_clean < date.today():
            self.add_error(None, 'Нельзя выполнять задания в прошлом!')
        if value_title_clean is None:
            raise ValidationError('Нененене')
        return cleaned_data