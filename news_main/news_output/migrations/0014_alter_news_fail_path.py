# Generated by Django 4.1.4 on 2023-01-13 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_output', '0013_pgsroomreserving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='fail_path',
            field=models.ImageField(null=True, upload_to='', verbose_name='Изображение'),
        ),
    ]