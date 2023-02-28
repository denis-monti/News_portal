from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активация')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещение о новых комментариях')
    slug = models.SlugField(max_length=255, unique=True, null=True, db_index=True, verbose_name="URL")

    def save(self, *args, **kwargs):
        super(AdvUser, self).save()
        if not self.slug:
            self.slug = self.username
            super(AdvUser, self).save()

    def delete(self, *args, **kwargs):
        for news in self.news_set.all():
            news.delete()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('users_info', kwargs = {"slug": self.slug})

    class Meta(AbstractUser.Meta):
        pass

class Follow(models.Model):
    user_id = models.ForeignKey('AdvUser', related_name='following_set', on_delete=models.CASCADE, verbose_name='Пользователь')
    followers = models.ForeignKey('AdvUser', related_name='followers_set', on_delete=models.CASCADE, verbose_name='подписка на пользователя ID')

    class Meta:
        unique_together = ('user_id', 'followers')
        verbose_name_plural = 'Список подписчиков'
        verbose_name = 'Подписчик пользователя'


class Message(models.Model):
    author = models.ForeignKey('AdvUser', related_name='user_message_set', on_delete=models.CASCADE, verbose_name='Пользователь')
    message = models.TextField(verbose_name='Содержание')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата сообщения')
    is_readed = models.BooleanField(default=False, verbose_name='Прочитано')
    dialog_id = models.ForeignKey('Dialog', on_delete=models.CASCADE, verbose_name='Id Дилога к которому относиться сообщение')


    class Meta:
        verbose_name_plural = 'Список сообщений'
        verbose_name = 'Сообщение'
        ordering = ['pub_date']

    def __str__(self):
        return self.message

class Dialog(models.Model):
    user1_id = models.ForeignKey('AdvUser', related_name='dialogue_participant_one', on_delete=models.CASCADE, verbose_name='Пользователь')
    user2_id = models.ForeignKey('AdvUser', related_name='dialogue_participant_two', on_delete=models.CASCADE,
                                 verbose_name='Пользователь')

    class Meta:
        verbose_name_plural = 'Список диалогов'
        verbose_name = 'Диалог'