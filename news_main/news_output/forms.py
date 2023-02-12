from django import forms
from captcha.fields import CaptchaField
# from localflavor.ru.forms import RUPassportNumberField
from .models import *
from django.core import validators
from django.forms import inlineformset_factory, formset_factory

class NewsForm(forms.ModelForm):
    captcha = CaptchaField(generator='captcha.helpers.math_challenge', label='Вычислите значение', error_messages={'invalid': 'Ошибка в вычислениях попробуйте ещё раз'})
    image = forms.ImageField(validators=[validators.FileExtensionValidator(
        allowed_extensions=('gif', 'jpg', 'png', 'jpeg'))],
        error_messages={
            'invalid_extension': 'Этот формат не поддерживаеться'},
        widget=forms.widgets.ClearableFileInput(attrs={'multiple': True}))
    # class Meta:
    #     model = News
    #     fields = ('title', 'description', 'file_path')

    class Meta:
        model = News
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

class AdditionalImageForm(forms.ModelForm):
    class Meta:
        model = AdditionalImage
        fields = '__all__'

class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(), empty_label=None,
        label='Надрубрика', required=True)


    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')

class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'news': forms.HiddenInput}

class CommentUserForm(forms.ModelForm):
    main_comment = forms.ModelChoiceField(
        queryset=Comment.objects.values_list('id', flat=True).filter(target_comment__isnull=True), empty_label=None,
        label='Главный коммент Ветки', required=True)
    target_comment = forms.ModelChoiceField(
        queryset=Comment.objects.all(), empty_label=None,
        label='Коммент ответ на коммент', required=True)

    class Meta:
        model = CommentUser
        fields = ('content', 'author', 'news',)


class CommentUserMainForm(forms.ModelForm):
    # target_comment = forms.ModelChoiceField(
    #     queryset=Comment.objects.all(), empty_label=None,
    #     label='Коммент ответ на коммент', required=True)
    main_comment = forms.ModelChoiceField(
        queryset=Comment.objects.values_list('id', flat=True).filter(target_comment__isnull=True), empty_label='---------',
        label='Главный коммент Ветки', required=False, widget=forms.HiddenInput)
    content = forms.CharField(label='Ваш комментарий', widget=forms.widgets.Textarea(attrs={'rows': '5', 'cols': '10' , 'style': 'resize:none;'}))

    class Meta:
        model = Comment
        fields = ('content', 'author', 'news', 'target_comment', 'main_comment')
        widgets = {'author': forms.HiddenInput, 'news': forms.HiddenInput, 'target_comment': forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    captcha = CaptchaField(generator='captcha.helpers.math_challenge', label='Вычислите значение',
                           error_messages={'invalid': 'Ошибка в вычислениях попробуйте ещё раз'})

    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'news': forms.HiddenInput}

class LikeDislikeForm(forms.ModelForm):

    class Meta:
        model = AdvUser
        fields = '__all__'

# class NewsFormEditDeleteAdd(forms.ModelForm):
#     class Meta:
#         model = News
#         fields = '__all__'
#         Widgets = {'author': forms.HiddenInput}

AIFormSet = inlineformset_factory(News, AdditionalImage, fields='__all__')
# AIFormSet = formset_factory(NewsForm, AdditionalImageForm)