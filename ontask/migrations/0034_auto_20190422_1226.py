# Generated by Django 2.2 on 2019-04-22 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0033_workflow_lusers_is_outdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='lusers_is_outdated',
            field=models.BooleanField(default=False),
        ),
    ]
