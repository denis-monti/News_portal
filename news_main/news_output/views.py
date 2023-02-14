import json
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.generic.dates import ArchiveIndexView, DateDetailView
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView, MultipleObjectTemplateResponseMixin, MultipleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail, mail_admins
from django.template.loader import render_to_string
from django.http import Http404
from django.utils.translation import gettext as _
from django.forms import  formset_factory
from datetime import datetime
from django.contrib import messages


import abc

from django.http import HttpResponse
# для поиск одна из двух в зависимости от иструмента поиска
# from elasticsearch_dsl import Q
from django.db.models import Q, Count

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from .documents import NewsDocument


from .models import *
from precise_bbcode.bbcode import get_parser

from django import forms
from django.contrib.auth.models import User
from .forms import *


# def index(request):
#     news_all = News.objects.all()
#     paginator = Paginator(news_all, 1)
#     if 'page' in request.GET:
#         page_num = request.GET['page']
#     else:
#         page_num = 1
#     page = paginator.get_page(page_num)
#     context = {'news_all': page.object_list, 'page': page}
#     template = get_template('news_output/22.html')
#     # return HttpResponse(template.render(context=context,
#     #                                     request=request))
#
#     return TemplateResponse(request, 'news_output/22.html',
#                             context=context)

# class NewsIndexView(ArchiveIndexView):
#     model = News
#     paginate_by = 3
#     date_field = 'published'
#     date_list_period = 'year'
#     template_name = 'news_output/index.html'
#     context_object_name = 'news_all'
#     allow_empty = True
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['rubrics'] = Rubric.objects.all()
#         return context

# def ajax_sorting(request):
#     print(request.GET)
#     print(request.GET['type_sort'])
#     print(request.GET['condition_button'])
#
#     if request.GET['condition_button'] == 'true':
#         news_all = News.objects.order_by(request.GET['type_sort']).all()
#     elif request.GET['condition_button'] == 'false':
#         news_all = News.objects.order_by('-' + request.GET['type_sort']).all()
#     else:
#         news_all = News.objects.all()
#
#     paginator = Paginator(news_all, 3)
#     if 'page' in request.GET:
#         page_num = request.GET['page']
#     else:
#         page_num = 1
#     page = paginator.get_page(page_num)
#     context = {'news_all': page.object_list, 'page': page}
#     template = get_template('news_output/22.html')
#     # return HttpResponse(template.render(context=context,
#     #                                     request=request))
#
#     return TemplateResponse(request, 'news_output/ajax_news_for_index.html',
#                             context=context)

class NewsIndexView(SuccessMessageMixin, ListView):
    model = News
    paginate_by = 2
    template_name = 'news_output/index.html'
    context_object_name = 'news_all'
    allow_empty = True

    def get_queryset(self):
        if self.kwargs['type_sort'] == 'default':
            # t = News.objects.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1)))
            # t = LikeDislike.objects.filter(news__in=y, is_like=1).filter(news__in=y, is_dislike=1)
            self.kwargs['type_sort'] = '-published'
        return News.objects.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by(self.kwargs['type_sort'])




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['like'] = LikeDislike.objects.values('news').filter(news__in=context['object_list'], is_like=1).annotate(total=Count('news')).order_by('-news__published')
        context['dislike'] = LikeDislike.objects.values_list('news').filter(news__in=context['object_list'], is_dislike=1).annotate(total=Count('news')).order_by('-news__published')
        # print(context['like'], context['dislike'], context['news_all'])
        return context

class NewsByRubricView(SingleObjectMixin, ListView):
    paginate_by = 2
    template_name = 'news_output/by_rubric.html'
    pk_url_kwarg = 'rubric_id'

    def get(self, request,  **kwargs):
        self.object = self.get_object(queryset=Rubric.objects.all())
        return super().get(request,  **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_rubric'] = self.object
        # context['rubrics'] = Rubric.objects.all()
        context['news_all'] = context['object_list']
        # date = datetime.today()
        # week = date.strftime("%V")
        # context['news_week_more_views'] = News.objects.filter(published__week=week)
        return context

    def get_queryset(self, **kwargs):
        if self.kwargs['type_sort'] == 'default':
            self.kwargs['type_sort'] = '-published'
        return self.object.news_set.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)),
              dislike=Count('likedislike',
                            filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by(self.kwargs['type_sort'])



class NewsCreateView(LoginRequiredMixin, CreateView):
    template_name = 'news_output/create.html'
    model = News
    form_class = NewsForm

    # def get_success_url(self):
    #     return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})

    # def get_form(self, form_class=None):
    #     return NewsForm(self.get_form_kwargs(), instance=self.object)

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        # form = NewsForm(request.POST, request.FILES)
        # if form.is_valid():
        #     form.save()
        formset = AIFormSet(request.POST, request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse_lazy('news_output:index'))
        else:
            formset = AIFormSet()
        return render(request, 'news_output/create.html', {'formset': formset})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = AIFormSet()
        return context



def profile_news_add(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=news)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'обьявление добавлено')
                return redirect('news_output:publication_user_auth', {'type_sort': 'default', 'user_id': request.user.id })
    else:
        form = NewsForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'news_output/create.html', context)


class NewsEditView(LoginRequiredMixin, UpdateView):
    template_name = 'news_output/edit_news.html'
    model = News
    form_class = NewsForm

    def get_success_url(self):
        return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        # form = NewsForm(request.POST, request.FILES)
        # if form.is_valid():
        #     form.save()
        formset = AIFormSet(request.POST, request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse_lazy('news_output:index'))
        else:
            formset = AIFormSet(instance=self.object)
        return render(request, 'news_output/create.html', {'formset': formset})

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        form = NewsForm(instance=self.object)
        formset = AIFormSet(instance=self.object)
        return render(request, 'news_output/create.html', {'formset': formset, 'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['form'] = NewsForm(initial={'author': self.request.user.pk})
        context['formset'] = AIFormSet()
        return context


def profile_news_change(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=news)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'обьявление добавлено')
                return redirect('news_output:index')
    else:
        form = NewsForm(instance=news)
        formset = AIFormSet(instanse=news)
    context = {'form': form, 'formset': formset}
    return render(request, 'news_output/edit_news.html', context)

class NewsDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'news_output/delete_news.html'
    model = News
    success_url = 'news_output/index'


    def get_success_url(self):
        return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class NewsDetailView(DetailView, CreateView):
    template_name = 'news_output/news_detail.html'
    model = News








    def get_form(self, form_class=None):
        initial = {'news': self.kwargs['pk']}
        if self.request.user.is_authenticated:
            initial['author'] = self.request.user.pk
            CommentUserMainForm(self.get_form_kwargs(), initial=initial, instance=self.object)
            return CommentUserMainForm(initial=initial)
        else:
            return None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentUserMainForm(self.request.POST)
        if form.is_valid():
            form.save()
            return redirect('news_output:detail', pk=self.object.pk)
        else:
            return redirect('news_output:detail', pk=self.object.pk)

    # def get_queryset(self):
    #     print(self.queryset.all())
    #     return News.objects.filter(id=self.object.pk).annotate(
    #         like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)),
    #         dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).first()

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()


        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk).annotate(
            like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)),
            dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None)))
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})


        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def get_page_comment(self):
        queryset = Comment.objects.filter(news=self.kwargs['pk'], is_active=True,
                                                     target_comment=None).annotate(
            like=Count('likedislike', filter=Q(likedislike__is_like=1)),
            dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('created_at')
        paginator = Paginator(queryset, 2)
        page = self.request.GET.get('page', 1)
        comment_all = paginator.get_page(page)
        return comment_all

    def get_context_data(self, **kwargs):
        parser = get_parser()
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()
        context['parsed_content'] = parser.render(context['news'].description)
        print(context['news'])
        context['ais'] = context['object'].additionalimage_set.all()
        context['comments'] = Comment.objects.filter(news=context['object'].id, is_active=True, target_comment=None).annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('created_at')
        context['comments_sub'] = Comment.objects.filter(news=context['object'].id, is_active=True).exclude(target_comment=None).annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('created_at')
        context['news_only_author'] = News.objects.filter(author=context['object'].author.pk)
        context['like'] = LikeDislike.objects.filter(news=context['object'].id, is_like=1).count()
        context['dislike'] = LikeDislike.objects.filter(news=context['object'].id, is_dislike=1).count()
        # comment = Comment.objects.filter(news=context['object'].id, is_active=True)
        # page: int = self.request.GET.get('page', 1)
        # p = Paginator(comment, 5)
        # context['page_comment'] = p.get_page(page)
        comment = self.get_page_comment()
        context['page_comment'] = comment
         # date = datetime.today()
        # week = date.strftime("%V")
        # context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context


def NewsDetail(request, pk):
    news = News.objects.get(pk=pk)
    ais = news.additionalimage_set.all()
    comments = Comment.objects.filter(news=pk, is_active=True, target_comment=None)
    comments_sub = Comment.objects.filter(news=pk, is_active=True).exclude(target_comment=None)
    len_comments = len(comments) + len(comments_sub)
    news_only_author = News.objects.filter(author=news.author.pk)
    initial = {'news': news.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.pk
        form_class = CommentUserMainForm
        form = form_class(initial=initial)
    else:
        form_class = None
        form = form_class
    if request.method == 'POST':
        print('h')
        if form_class(request.POST).is_valid():
            form_class(request.POST).save()
            return redirect('news_output:detail', pk=news.pk)
        # if form_class(request.POST).is_valid():
        #     form_class(request.POST).save()
        #     messages.add_message(request, messages.SUCCESS,
        #                          'Комментарий добавлен')
        # else:
        #     form = form_class(request.POST)
        #     messages.add_message(request, messages.WARNING,
        #                          'Комментарий не добавлен')
    context = {'news': news, 'ais': ais, 'len_comments': len_comments, 'comments': comments, 'comments_sub': comments_sub, 'news_only_author': news_only_author, 'form': form}
    return render(request, 'news_output/news_detail.html', context)


# class PublicationUser(SingleObjectMixin, ListView):
#     paginate_by = 1
#     template_name = 'news_output/publication_user.html'
#     pk_url_kwarg = 'user_id'
#
#     def get(self, request, **kwargs):
#         self.object = self.get_object(queryset=AdvUser.objects.all())
#         return super().get(request, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context['current_rubric'] = self.object
#         # context['rubrics'] = Rubric.objects.all()
#         context['news_all'] = context['object_list']
#         # date = datetime.today()
#         # week = date.strftime("%V")
#         # context['news_week_more_views'] = News.objects.filter(published__week=week)
#         return context
#
#     def get_queryset(self, **kwargs):
#         if self.kwargs['type_sort'] == 'default':
#             return self.object.news_set.all()
#         else:
#             return self.object.news_set.order_by(self.kwargs['type_sort']).all()


class PublicationUser(LoginRequiredMixin, ListView):
    paginate_by = 1
    template_name = 'news_output/publication_user.html'
    context_object_name = 'news_all'

    def get_queryset(self, **kwargs):
        if self.kwargs['type_sort'] == 'default':
            self.kwargs['type_sort'] = '-published'
        return News.objects.filter(author_id=self.kwargs['user_id']).annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)),
                  dislike=Count('likedislike',
                                filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by(self.kwargs['type_sort']).all()



class SearchNews(ListView, forms.Form):
    model = News
    paginate_by = 1
    template_name = 'news_output/search.html'
    context_object_name = 'news_all'
    allow_empty = True
    form_class = SearchForm


    def get_queryset(self):
        query = self.request.GET.get('query')
        q = Q(title__icontains=query) | Q(description__icontains=query)
        if self.kwargs['type_sort'] == 'default':
            return News.objects.filter(q)
        return (News.objects.order_by(self.kwargs['type_sort'])).filter(q)
        # return News.objects.all()

    # для elasticsearch:
    # def get_queryset(self):
    #     news = NewsDocument.search().query("multi_match", fields=['title', 'description'], query=self.request.GET.get('query'), fuzziness='auto')
    #     if self.kwargs['type_sort'] == 'default':
    #         return news.to_queryset()
    #     return news.to_queryset().order_by(self.kwargs['type_sort'])
    #     # return News.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()
        context['search_text'] = self.request.GET.get('query')
        # date = datetime.today()
        # week = date.strftime("%V")
        # context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context

@csrf_exempt
def AjaxLikeDislike(request):
    user = AdvUser.objects.get(id=request.user.pk)
    resp = HttpResponse("", content_type='text/plain; charset=utf- 8', status=200)
    try:
        if request.POST['target_comment'] == 'comment':
            comment = Comment.objects.get(id=request.POST['id'])
            news = comment.news
            checking = LikeDislike.objects.filter(author=user.id, news=news.pk, target_comment=comment.id).first()
            if request.user.pk != comment.author.id:
                if request.POST['type'] == 'like':
                    if checking == None:
                        like_and_dislike = LikeDislike()
                        like_and_dislike.news = news
                        like_and_dislike.target_comment = comment
                        like_and_dislike.author = user
                        like_and_dislike.is_like = 1
                        like_and_dislike.is_dislike = 0
                        like_and_dislike.save()
                        resp.write('1, 0')
                        return resp
                    elif checking.is_like == 0:
                        checking.is_like = 1
                        checking.is_dislike = 0
                        checking.save()
                        resp.write('1, -1')
                        return resp
                    else:
                        checking.delete()
                        resp.write('-1, 0')
                        return resp
                elif request.POST['type'] == 'dislike':
                    if checking == None:
                        like_and_dislike = LikeDislike()
                        like_and_dislike.news = news
                        like_and_dislike.target_comment = comment
                        like_and_dislike.author = user
                        like_and_dislike.is_like = 0
                        like_and_dislike.is_dislike = 1
                        like_and_dislike.save()
                        resp.write('0, 1')
                        return resp
                    elif checking.is_dislike == 0:
                        checking.is_like = 0
                        checking.is_dislike = 1
                        checking.save()
                        resp.write('-1, 1')
                        return resp
                    else:
                        checking.delete()
                        resp.write('0, -1')
                        return resp
                else:
                    resp.write('0, 0')
                    return resp
            else:
                resp.write('0, 0')
                return resp
        elif request.POST['target_comment'] == 'publication':
            news = News.objects.get(id=request.POST['id'])
            checking = LikeDislike.objects.filter(author=user.id, news=news.pk, target_comment=None).first()
            if request.user.pk != news.author.id:
                if request.POST['type'] == 'like':
                    if checking == None:
                        like_and_dislike = LikeDislike()
                        like_and_dislike.news = news
                        like_and_dislike.author = user
                        like_and_dislike.is_like = 1
                        like_and_dislike.is_dislike = 0
                        like_and_dislike.save()
                        resp.write('1, 0')
                        return resp
                    elif checking.is_like == 0:
                        checking.is_like = 1
                        checking.is_dislike = 0
                        checking.save()
                        resp.write('1, -1')
                        return resp
                    else:
                        checking.delete()
                        resp.write('-1, 0')
                        return resp
                elif request.POST['type'] == 'dislike':
                    if checking == None:
                        like_and_dislike = LikeDislike()
                        like_and_dislike.news = news
                        like_and_dislike.author = user
                        like_and_dislike.is_like = 0
                        like_and_dislike.is_dislike = 1
                        like_and_dislike.save()
                        resp.write('0, 1')
                        return resp
                    elif checking.is_dislike == 0:
                        checking.is_like = 0
                        checking.is_dislike = 1
                        checking.save()
                        resp.write('-1, 1')
                        return resp
                    else:
                        checking.delete()
                        resp.write('0, -1')
                        return resp
                else:
                    resp.write('0, 0')
                    return resp
            else:
                resp.write('0, 0')
                return resp
    except:
        resp.write('0, 0')
        return resp





