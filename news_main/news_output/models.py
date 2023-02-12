from django.db import models
from django.contrib.auth.models import User, AbstractUser

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, DateTimeRangeField

from django.contrib.postgres.validators import RangeMaxValueValidator, RangeMinValueValidator
from easy_thumbnails.fields import ThumbnailerImageField, ImageField
from datetime import datetime
from django.dispatch import Signal
from django.db.models.signals import post_save
from .utilites import *
from news_auth_registered.models import AdvUser



class News(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    rubric = models.ForeignKey('SubRubric',
                               on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=50, verbose_name='Заголовок', unique=True,
                             error_messages={'unique': 'Такой Заголовок уже есть'})
    description = models.TextField(verbose_name='Описание Новости', error_messages={'null': 'Поле не заполнено'})
    tag_news = models.CharField(null=True, max_length=100, verbose_name='Ключевые слова')
    image = ImageField(upload_to='get_timestamp_path', null=True, blank=True, verbose_name='Изображение')
    author = models.ForeignKey('news_auth_registered.AdvUser', default='0', on_delete=models.CASCADE, verbose_name='Автор статьи')
    # is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')


    def delete(self, *args, **kwargs):
        # self.file_path.delete(save=False)
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return '/news_output/detail/%s/' % self.pk

    class Meta:
        verbose_name_plural = 'Список новостей'
        verbose_name = 'Новость'
        ordering = ['-published']
        # constraints = (
        #     models.UniqueConstraint(fields=('title', 'description'),
        #     name='%(app_label)s_%(class)s_title_description_constraint'),)
        get_latest_by = 'published'

class AdditionalImage(models.Model):
    news = models.ForeignKey('News', on_delete=models.CASCADE, verbose_name='Обьявление')

    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


class Rubric(models.Model):
    # parent_id =
    # level =
    name = models.CharField(max_length=30, db_index=True, unique=True, verbose_name='Название')
    # description = models.TextField(null=True, max_length=100, verbose_name='Описание рубрики', error_messages={'null': 'Поле не заполнено'})
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Надрубрика')

    def get_absolute_url(self):
        return "/news_output/%s/" % self.pk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']

class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)

class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE,
                             verbose_name='Статья', null=True)
    target_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Автор комментария к которому пишется ответ')
    main_comment = models.IntegerField(null=True, blank=True, db_index=True, verbose_name='Id главного родителя для веток комментов')
    author = models.ForeignKey('news_auth_registered.AdvUser', default='0', on_delete=models.CASCADE,
                              verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['created_at']

class CommentPublicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(target_comment__isnull=True)

class CommentPublication(Comment):
    object = CommentPublicationManager()

    def __str__(self):
        return '%s - %s' % (self.news.title, self.author)

    class Meta:
        proxy = True
        ordering = ('created_at',)
        verbose_name = 'Комментарий к статье'
        verbose_name_plural = 'Комментарии к статьям'

class CommentUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(target_comment__isnull=False)

class CommentUser(Comment):
    objects = CommentUserManager()

    def __str__(self):
        return '%s - %s - %s - %s - %s' % (self.news.title, self.target_comment.author.username, self.author, self.main_comment, self.pk)

    class Meta:
        proxy = True
        ordering = ('created_at',)
        verbose_name = 'Ответ на комментарий'
        verbose_name_plural = 'Ответы на комментарии'


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].news.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)


class LikeDislike(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE,
                             verbose_name='Статья к которой относиться лайк', null=True)
    target_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True,
                                       verbose_name='комментарий к которому поставлен лайк')
    author = models.ForeignKey('news_auth_registered.AdvUser', default='0', on_delete=models.CASCADE,
                               verbose_name='Пользователь поставивший лайк')
    is_like = models.BooleanField(default=False, verbose_name='Лайки')
    is_dislike = models.BooleanField(default=False, verbose_name='Дизлайки')

    class Meta:
        verbose_name_plural = 'Список лайков'
        verbose_name = 'Лайки и дизлайки'
        ordering = ('-news__published',)
# class PGSRoomReserving(models.Model):
#     reserving = DateTimeRangeField(
#         verbose_name= 'Bpeмя резервирования',
#         validators= [
#             RangeMinValueValidator(limit_value=datetime(1900, 1, 1)),
#             RangeMaxValueValidator(limit_value=datetime(3000, 1, 1)),
#             ])

# class AdvUser(models.Model):
#     is_activated = models.BooleanField(default=True)
#     user = models.OneToOneField(User, on_delete=models.CASCADE)


# class User(models.Model):
#     id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
#     username = models.CharField(db_index=True, unique=True, max_length=15, verbose_name='Имя пользователя',
#                              error_messages={'invalid': 'Неправильное имя пользователя'})
#     email = models.EmailField(unique=True, verbose_name='Почта пользователя')
#     password_hash = models.CharField(max_length=15)
#     last_seen =
#     avatar_path = models.TextField(verbose_name='Пути для аватарок')
#
# class Comment(models.Model):
#     id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
#     author_id =
#     news_id =
#     description =
#     published =
#
# class like_dislike(models.Model):
#     id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
#     object_id =
#     type_object =
#     user_id =
#     like =
#     dislike =