# Generated by Django 5.1.1 on 2024-10-07 12:30

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_alter_project_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='name',
            field=models.CharField(default='Default Session Name', max_length=255),
        ),
        migrations.AlterField(
            model_name='project',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, default='https://res.cloudinary.com/dwzqcmaod/image/upload/v1728120693/neon2_r6qoo1.png', max_length=255, null=True, verbose_name='image'),
        ),
    ]
