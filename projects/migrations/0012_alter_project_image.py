# Generated by Django 5.1.1 on 2024-10-05 09:32

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_alter_project_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, default='https://res-console.cloudinary.com/dwzqcmaod/thumbnails/v1/image/upload/v1728120693/bmVvbjJfcjZxb28x/preview', max_length=255, null=True, verbose_name='image'),
        ),
    ]
