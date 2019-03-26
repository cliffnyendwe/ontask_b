# Generated by Django 2.1.7 on 2019-02-28 09:23

from django.db import migrations


def create_triplets(apps, schema_editor):
    """
    Traverse every action and for every column in the columns field, transform
    it into a triplet (action, column, NULL) and insert it into the new
    ActionColumnConditionTuple table

    :param apps:
    :param schema_editor:
    :return:
    """

    Action = apps.get_model('action', 'Action')
    ActionColumnConditionTuple = apps.get_model('action',
                                                'ActionColumnConditionTuple')
    for action in Action.objects.all():
        # Processing one action
        for column in action.columns.all():
            # Processing a column
            obj, created = ActionColumnConditionTuple.objects.get_or_create(
                action=action,
                column=column,
                condition=None
            )


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0049_auto_20190228_1953'),
    ]

    operations = [
        migrations.RunPython(create_triplets),
    ]