# Generated by Django 4.1.4 on 2023-01-15 07:27

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news_output', '0021_alter_news_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='file_path',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='news_img', verbose_name='Изображение'),
        ),
    ]
