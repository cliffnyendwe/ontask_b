# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-27 11:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0027_auto_20180826_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledaction',
            name='type',
            field=models.CharField(choices=[('email_send', 'Send emails'), ('json_send', 'Send JSON objects')], max_length=256),
        ),
    ]
