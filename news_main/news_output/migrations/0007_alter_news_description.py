# Generated by Django 4.1.4 on 2022-12-27 14:43

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_output', '0006_news_tag_news_alter_news_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='description',
            field=ckeditor.fields.RichTextField(error_messages={'null': 'Поле не заполнено'}, verbose_name='Описание Новости'),
        ),
    ]
