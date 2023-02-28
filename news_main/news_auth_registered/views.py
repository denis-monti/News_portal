from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail, mail_admins
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.core.signing import BadSignature
from .models import *
from .forms import *
from .utilites import signer
from django.db.models import Q, Count



class Login(LoginView):
    template_name = "news_auth_registered/login.html"
    form_class = AuthenticationForm
    # next_page = 'news_output:index'
    extra_context = {'auth': 0}


class PasswordChange(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = "news_auth_registered/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("news_auth_registered:password_change_done")
    success_message = 'Пароль пользователя изменен'
    extra_context = {'auth': 0}


class PasswordResetSend(PasswordResetView, EmailMultiAlternatives):
    template_name = "news_auth_registered/password_reset_form.html"
    subject_template_name = "email/reset_subject.txt"
    email_template_name = "email/reset_email.txt"
    form_class = PasswordResetCustomForm
    # email_template_name = ""
    success_url = reverse_lazy("news_auth_registered:password_reset_done")
    extra_context = {'auth': 0}


class ProfileSetting(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AdvUser
    template_name = "news_auth_registered/profile_setting.html"
    form_class = EditUserForm
    success_url = reverse_lazy('news_output:index')
    success_message = 'Данные ползователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class RegisterUserView(LoginRequiredMixin, CreateView):
    model = AdvUser
    template_name = 'news_auth_registered/register_user.html'
    form_class = RegisterUserForm
    # success_url = reverse_lazy('news_auth_registered:register_done')

    def get_success_url(self):
        return reverse_lazy('news_auth_registered:register_done')

class RegisterDoneView(TemplateView):
    template_name = 'news_auth_registered/register_done.html'

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'news_auth_registered/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'news_auth_registered/user_is_activated.html'
    else:
        template = 'news_auth_registered/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'news_auth_registered/delete_user.html'
    success_url = reverse_lazy('news_output:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'news_auth_registered/password_reset_confirm.html'
    extra_context = {'auth': 0}
    success_url = reverse_lazy("news_auth_registered:password_reset_complete")

class Conversations(LoginRequiredMixin, ListView):
    template_name = 'news_auth_registered/conversations_list.html'
    model = Dialog
    extra_context = {'auth': 0}
    paginate_by = 2


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = context['object_list']
        for i in context['data']:
            print(i.message_set.last())
        # context['followers/following'] = AdvUser.objects.filter(id=context['object'].pk).annotate(following=Count('follow', filter=Q(follow__user_id=context['user_detail'])), followers=Count('follow', filter=Q(follow__followers=context['user_detail'].pk)))
        return context

    def get_queryset(self, **kwargs):
        self.object = AdvUser.objects.get(pk=self.request.user.pk)
        dialog_list = self.object.dialogue_participant_one.all()
        dialog_sender = self.object.dialogue_participant_two.all()
        dialog_list |= dialog_sender
        return dialog_list


class Dialog(LoginRequiredMixin, ListView, DetailView, CreateView):
    template_name = 'news_auth_registered/dialog_message.html'
    model = AdvUser
    extra_context = {'auth': 0}

    def get_form(self, form_class=None):
        initial = {'dialog_id': self.kwargs['dialog_id']}
        if self.request.user.is_authenticated:
            initial['author'] = self.request.user.pk
            Message(self.get_form_kwargs(), initial=initial, instance=self.object)
            return Message(initial=initial)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_detail'] = AdvUser.objects.get(pk=context['object'].pk)
        context['data'] = context['object_list']
        context['type_data'] = self.kwargs['slug']
        return context


    def get_queryset(self, **kwargs):
        self.object = AdvUser.objects.get(username=self.kwargs['slug'])
        # return self.object.news_set.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by('-published')
        dialog_recipient = self.object.dialogue_participant_one.filter(user2_id=self.request.user.pk)
        dialog_sender = self.object.dialogue_participant_two.filter(user1_id=self.request.user.pk)
        if dialog_recipient.exists():
            dialog = dialog_recipient[0].message_set.all()
        elif dialog_sender.exists():
            dialog = dialog_sender[0].message_set.all()
        return dialog

