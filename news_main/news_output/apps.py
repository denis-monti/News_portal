from django.apps import AppConfig


class NewsOutputConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_output'
    verbose_name = 'Вывод новостей'
