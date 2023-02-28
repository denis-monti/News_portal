from django.contrib import admin
from .models import *
import datetime
from django import forms
from .utilites import send_activation_notification

def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с требованиями отправлены')
send_activation_notifications.short_description = 'Отправка писем с требованием активации'

class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        )


    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False,
                date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False,
                date_joined__date__lt=d)

class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'firstname', 'last_name', 'slug')
    list_filter = (NonactivatedFilter,)
    fields = (('username', 'email', 'slug'), ('first_name', 'last_name'),
    ('send_messages', 'is_active', 'is_activated'),
    ('is_staff', 'is_superuser'),
     'groups', 'user_permissions',
    ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)

class FollowAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'followers')
    search_fields = ('user_id', 'followers')
    fields = ('user_id', 'followers',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'message', 'dialog_id')
    search_fields = ('author', 'message')
    fields = ('author', 'message', 'dialog_id', 'is_readed',)

class DialogAdmin(admin.ModelAdmin):
    list_display = ('user1_id', 'user2_id')
    search_fields = ('user1_id', 'user2_id')
    fields = ('user1_id', 'user2_id',)


# class AdvUserAdmin(admin.ModelAdmin):
#     list_display = ('__all__',)

admin.site.register(Message, MessageAdmin)
admin.site.register(Dialog, DialogAdmin)
admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Follow, FollowAdmin)

