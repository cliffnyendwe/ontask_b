# Generated by Django 2.2.5 on 2019-10-01 22:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0036_remove_sqlconnection_db_password'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sqlconnection',
            old_name='db_password2',
            new_name='db_password',
        ),
    ]
