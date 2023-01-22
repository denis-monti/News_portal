from django import forms
from captcha.fields import CaptchaField
# from localflavor.ru.forms import RUPassportNumberField
from .models import News
from django.core import validators

class NewsForm(forms.ModelForm):
    captcha = CaptchaField(generator='captcha.helpers.math_challenge', label='Вычислите значение', error_messages={'invalid': 'Ошибка в вычислениях попробуйте ещё раз'})
    file_path = forms.ImageField(validators=[validators.FileExtensionValidator(
        allowed_extensions=('gif', 'jpg', 'png', 'jpeg'))],
        error_messages={
            'invalid_extension': 'Этот формат не поддерживаеться'},
        widget=forms.widgets.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = News
        fields = ('title', 'description', 'rubric', 'file_path')

# class Formm(forms.ModelForm):
#     class Meta:
#         model = PGSRoomReserving
#         fields = ('reserving',)

# class ff(forms.Form):
#     I = RUPassportNumberField()
