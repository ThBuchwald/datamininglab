from django.core.management import call_command
from django.db import migrations


def forwards_func(apps, schema_editor):
    fixture_labels = ['auth_permission.json', 'auth_group.json']
    call_command('loaddata', *[
        'main/fixtures/{}'.format(fixture)
        for fixture in fixture_labels
    ])


def reverse_func(apps, schema_editor):
    models = [
        apps.get_model("main", model_name)
        for model_name in ['Group', 'Permission']
    ]
    for model in models:
        model.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_populate_sampletypes'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]