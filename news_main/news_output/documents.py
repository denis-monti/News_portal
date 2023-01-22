from django.contrib.auth.models import User
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import *


@registry.register_document
class NewsDocument(Document):

    class Index:
        name = 'news'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = News
        fields = [
            'id',
            'title',
            'description',
            'published',
        ]
