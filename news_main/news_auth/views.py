from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail, mail_admins

class Login(LoginView):
    template_name = "news_auth/login.html"
    form_class = AuthenticationForm
    # next_page = 'news_output:index'
    extra_context = {'auth': 0}


class PasswordChange(PasswordChangeView):
    template_name = "news_auth/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("news_auth:password_change_done")
    extra_context = {'auth': 0}


class PasswordResetSend(PasswordResetView, EmailMultiAlternatives):
    template_name = "news_auth/password_reset_form.html"
    subject_template_name = "news_auth/reset_subject.txt"
    email_template_name = "news_auth/reset_email.txt"
    form_class = PasswordResetForm
    email_template_name = ""
    success_url = reverse_lazy("news_auth:password_reset_done")
    extra_context = {'auth': 0}
    # s = render_to_string(email_template_name, extra_context)
    # em = EmailMultiAlternatives(subject='Запрос на сброс пароля', body=s, to=['d.matin.k@yandex.ru'])
    #em.attach_alternative()
    # em.send()
    # send_mail('Запрос на сброс пароля', email_template_name, from_email='karkalak@mail.ru', recipient_list=['d.matin.k@yandex.ru'])
    # mail_admins('Подьём', 'gdfg')

