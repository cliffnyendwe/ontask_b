# Generated by Django 2.1.3 on 2018-12-12 01:23

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0041_auto_20181207_0539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condition',
            name='formula',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True, verbose_name='formula'),
        ),
    ]
