# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-08 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0007_auto_20171208_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='Valid from',
            field=models.DateTimeField(default=None, null=True, verbose_name='Column valid from'),
        ),
        migrations.AlterField(
            model_name='column',
            name='Valid until',
            field=models.DateTimeField(default=None, null=True, verbose_name='Column valid until'),
        ),
    ]
