from django.db import models
from django.contrib.auth.models import AbstractUser

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активация')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещение о новых комментариях')

    def delete(self, *args, **kwargs):
        for news in self.news_set.all():
            news.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass
