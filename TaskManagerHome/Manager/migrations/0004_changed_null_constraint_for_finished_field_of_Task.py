# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-22 00:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Manager', '0003_added_finished_field_to_Task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='finished',
            field=models.DateField(null=True),
        ),
    ]
