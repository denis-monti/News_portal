from django.apps import AppConfig
from django.dispatch import Signal
from .utilites import send_activation_notification, send_reset_password

class NewsAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_auth_registered'

user_registered = Signal()

def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registered.connect(user_registered_dispatcher)


reset_password = Signal()

def user_reset_password(sender, **kwargs):
    send_reset_password(kwargs['instance'])

reset_password.connect(user_reset_password)