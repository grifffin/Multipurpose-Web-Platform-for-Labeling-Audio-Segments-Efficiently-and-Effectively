# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-25 19:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_study_max_responses_per_worker'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='final_label',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Label'),
        ),
        migrations.AlterField(
            model_name='response',
            name='label_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
