# Generated by Django 4.1.4 on 2023-01-13 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_output', '0014_alter_news_fail_path'),
    ]

    operations = [
        migrations.RenameField(
            model_name='news',
            old_name='fail_path',
            new_name='file_path',
        ),
    ]
