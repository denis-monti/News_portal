import json
from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic.dates import ArchiveIndexView, DateDetailView
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail, mail_admins
from django.template.loader import render_to_string

from datetime import datetime
from django.contrib import messages

<<<<<<< HEAD

from .serializers import RubricSerializer
=======
>>>>>>> e2147defc2401c88eeef7eac9411b5da21982db5
import abc

from django.http import HttpResponse
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from .documents import NewsDocument


from .models import *
from precise_bbcode.bbcode import get_parser

from django import forms
from django.contrib.auth.models import User
from .models import *
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


from django.core.cache import cache
from .models import Rubric
import redis
class NewsIndexView(SuccessMessageMixin, ListView):
    model = News
    paginate_by = 3
    template_name = 'news_output/index.html'
    context_object_name = 'news_all'
    allow_empty = True

    def get_queryset(self):
        if self.kwargs['type_sort'] == 'default':
            return News.objects.all()
        return News.objects.order_by(self.kwargs['type_sort'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()
        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)
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
        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)
        return context

    def get_queryset(self, **kwargs):
        if self.kwargs['type_sort'] == 'default':
            return self.object.news_set.all()
        else:
            return self.object.news_set.order_by(self.kwargs['type_sort']).all()

class NewsCreateView(LoginRequiredMixin, CreateView):
    template_name = 'news_output/create.html'
    # model = News

    # fields = ['title', 'description', 'rubric']
    form_class = NewsForm
    # success_url = '/news_output/{rubric_id}'
    # success_url = reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': object.rubric_id})

    def get_success_url(self):
        return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()

        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context

class NewsEditView(UpdateView):
    template_name = 'news_output/update_news.html'
    model = News
    form_class = NewsForm



    def get_success_url(self):
        return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()

        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context

class NewsDetailView(DetailView):
    model = News


    def get_context_data(self, **kwargs):
        parser = get_parser()
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()
        context['parsed_content'] = parser.render(context['news'].description)
        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context

class SearchNews(ListView, forms.Form):
    model = News
    paginate_by = 3
    template_name = 'news_output/search.html'
    context_object_name = 'news_all'
    allow_empty = True


    def get_queryset(self):
        news = NewsDocument.search().query("multi_match", fields=['title', 'description'], query=self.request.GET.get('query'), fuzziness='auto')
        if self.kwargs['type_sort'] == 'default':
            return news.to_queryset()
        return news.to_queryset().order_by(self.kwargs['type_sort'])
        # return News.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rubrics'] = Rubric.objects.all()
        context['search_text'] = self.request.GET.get('query')

        date = datetime.today()
        week = date.strftime("%V")
        context['news_week_more_views'] = News.objects.filter(published__week=week)

        return context


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['GET', 'POST'])
def api_rubrics(request):
    if request.method == 'GET':
        rubrics = Rubric.objects.all()
        serializer = RubricSerializer(rubrics, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RubricSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_rubric_detail(request, pk):
    rubric = Rubric.objects.get(pk=pk)
    if request.method == 'GET':
        serializer = RubricSerializer(rubric)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = RubricSerializer(rubric, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        rubric.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

