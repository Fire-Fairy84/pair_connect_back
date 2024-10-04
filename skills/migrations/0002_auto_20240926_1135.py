from django.db import migrations


def create_default_stacks(apps, schema_editor):
    Stack = apps.get_model('skills', 'Stack')
    Stack.objects.create(name='Fullstack')
    Stack.objects.create(name='Backend')
    Stack.objects.create(name='Frontend')


class Migration(migrations.Migration):
    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_stacks),
    ]
