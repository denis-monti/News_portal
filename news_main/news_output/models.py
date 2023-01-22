from django.db import models
from django.contrib.auth.models import User

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, DateTimeRangeField

from django.contrib.postgres.validators import RangeMaxValueValidator, RangeMinValueValidator
from easy_thumbnails.fields import ThumbnailerImageField
from datetime import datetime
from django.dispatch import Signal





class News(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    # user_id = models.ForeignKey('User', on_delete=models.PROTECT, verbose_name='Пользователь')
    title = models.CharField(max_length=50, verbose_name='Заголовок', unique=True,
                             error_messages={'unique': 'Такой Заголовок уже есть'})
    description = models.TextField(verbose_name='Описание Новости', error_messages={'null': 'Поле не заполнено'})
    tag_news = models.CharField(null=True, max_length=100, verbose_name='Ключевые слова')
    file_path = ThumbnailerImageField(upload_to='news_img', null=True, blank=True, verbose_name='Изображение')
    rubric = models.ForeignKey('Rubric', null=True,
                               on_delete=models.PROTECT, verbose_name='Рубрика')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name_plural = 'Список новостей'
        verbose_name = 'Новость'
        ordering = ['-published']
        # constraints = (
        #     models.UniqueConstraint(fields=('title', 'description'),
        #     name='%(app_label)s_%(class)s_title_description_constraint'),)
        get_latest_by = 'published'

    def delete(self, *args, **kwargs):
        self.file_path.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

<<<<<<< HEAD
    def get_absolute_url(self):
        return '/news_output/detail/%s/' % self.pk

=======
>>>>>>> e2147defc2401c88eeef7eac9411b5da21982db5
class Rubric(models.Model):
    # parent_id =
    # level =
    name = models.CharField(max_length=30, db_index=True, verbose_name='Название')
    description = models.TextField(null=True, max_length=100, verbose_name='Описание рубрики', error_messages={'null': 'Поле не заполнено'})

    def get_absolute_url(self):
        return "/news_output/%s/" % self.pk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']

class Profile(models.Model):
    phone = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)




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