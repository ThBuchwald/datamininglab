from django.db import migrations

def create_sample_types(apps, schema_editor):
    SampleType = apps.get_model('main', 'SampleType')
    SampleType.objects.create(name="Battery")
    SampleType.objects.create(name="Solids")
    SampleType.objects.create(name="Liquid")
    SampleType.objects.create(name="Suspension")

def delete_sample_types(apps, schema_editor):
    SampleType = apps.get_model('main', 'SampleType')
    SampleType.objects.all().delete()



class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),  # Replace with the appropriate dependency
    ]

    operations = [
        migrations.RunPython(create_sample_types, delete_sample_types),
    ]