# Generated by Django 4.1.4 on 2023-01-13 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_output', '0015_rename_fail_path_news_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='tag_news',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ключевые слова'),
        ),
    ]