from django import forms
from captcha.fields import CaptchaField
# from localflavor.ru.forms import RUPassportNumberField
from .models import AdvUser
from django.core import validators
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .apps import user_registered, reset_password
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm

class EditUserForm(forms.ModelForm):
    # captcha = CaptchaField(generator='captcha.helpers.math_challenge', label='Вычислите значение', error_messages={'invalid': 'Ошибка в вычислениях попробуйте ещё раз'})
    # file_path = forms.ImageField(validators=[validators.FileExtensionValidator(
    #     allowed_extensions=('gif', 'jpg', 'png', 'jpeg'))],
    #     error_messages={
    #         'invalid_extension': 'Этот формат не поддерживаеться'},
    #     widget=forms.widgets.ClearableFileInput(attrs={'multiple': True}))
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')

class PasswordResetCustomForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    def clean_email(self):

        email = self.cleaned_data['email']
        if email:
            validate_email(email)
            if not AdvUser.objects.exclude(email=email):
                raise ValidationError('Пользователь с данным email не найден',
                                      code='email_user_not_found')
        return email

    def save(self, commit=False, *args, **kwargs):
        t = super().save(commit=False)
        reset_password.send(PasswordResetCustomForm, instance=t)

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data['password1'])
    #     user.is_active = False
    #     user.is_activated = False
    #     if commit:
    #         user.save()
    #     user_registered.send(RegisterUserForm, instance=user)


    class Meta:
        model = AdvUser
        fields = ('email',)

class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='введите тот же самый пароль еще раз для проверки')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            validate_email(email)
            if AdvUser.objects.filter(email=email):
                raise ValidationError('Пользователь с данным email уже зарегистрирован, попробуйте восстановить пароль',
                    code='email_already_exists')
        return email

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                'Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)


    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_messages')
