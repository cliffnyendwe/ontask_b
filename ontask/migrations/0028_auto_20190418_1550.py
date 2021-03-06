# Generated by Django 2.2 on 2019-04-18 06:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ontask', '0027_auto_20190418_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='lusers',
            field=models.ManyToManyField(related_name='workflows_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflows_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
