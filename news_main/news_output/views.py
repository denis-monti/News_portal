from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.utils.translation import gettext as _
from django.contrib import messages




from django.http import HttpResponse
# для поиск одна из двух в зависимости от иструмента поиска
# from elasticsearch_dsl import Q
from django.db.models import Q, Count



from precise_bbcode.bbcode import get_parser
from news_auth_registered.models import Follow, AdvUser
from .forms import *


class NewsIndexView(SuccessMessageMixin, ListView):
    model = News
    paginate_by = 2
    template_name = 'news_output/index.html'
    context_object_name = 'news_all'
    allow_empty = True

    def get_queryset(self):
        if self.kwargs['type_sort'] == 'default':
            self.kwargs['type_sort'] = '-published'
        return News.objects.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by(self.kwargs['type_sort'])




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['news_all'] = context['object_list']
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

    def get_form(self, form_class=None):
        initial = {}
        if self.request.user.is_authenticated:
            initial['author'] = self.request.user.pk
            return NewsForm(initial=initial)
        else:
            return None

    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            news = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=news)
            if formset.is_valid():
                formset.save()
                return redirect('news_output:index')
            formset = AIFormSet()
            return render(request, 'news_output/create.html', {'form': form, 'formset': formset})
        else:
            formset = AIFormSet()
            return render(request, 'news_output/create.html', { 'form': form, 'formset': formset})


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

    def get_success_url(self):
        return reverse_lazy('news_output:by_rubric', kwargs={'rubric_id': self.object.rubric_id})


    def get_form(self, form_class=None):
        if self.request.user.is_authenticated:
            return NewsForm(instance=self.object)
        else:
            return None



    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        form = NewsForm(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            news = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=news)
            if formset.is_valid():
                formset.save()
                return redirect('news_output:index')
            else:
                form = NewsForm(instance=self.object)
                formset = AIFormSet(instance=self.object)
                return render(request, 'news_output/edit_news.html', {'form': form, 'formset': formset})
        else:
            form = NewsForm(instance=self.object)
            formset = AIFormSet(instance=self.object)
        return render(request, 'news_output/edit_news.html', {'formset': formset, 'form': form})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = AIFormSet(instance=self.object)
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
        if self.kwargs['only_comment'] == False:
            paginator = Paginator(queryset, 2)
            page = self.request.GET.get('page', 1)
            comment_all = paginator.get_page(page)
        elif self.kwargs['only_comment'] == True:
            comment_all = queryset
        return comment_all

    def get_context_data(self, **kwargs):
        parser = get_parser()
        context = super().get_context_data(**kwargs)
        context['parsed_content'] = parser.render(context['news'].description)
        context['only_comment'] = self.kwargs['only_comment']
        context['ais'] = context['object'].additionalimage_set.all()
        # context['comments'] = Comment.objects.filter(news=context['object'].id, is_active=True, target_comment=None).annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('created_at')
        context['comments_sub'] = Comment.objects.filter(news=context['object'].id, is_active=True).exclude(target_comment=None).annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('created_at')
        context['news_only_author'] = News.objects.filter(author=context['object'].author.pk, rubric=context['news'].rubric).annotate(active=Count('likedislike', filter=Q(likedislike__target_comment=None))).filter(active__gt=1).exclude(id=context['news'].id)[:5]
        if self.request.user.is_authenticated:
            context['subrciption'] = Follow.objects.filter(user_id=self.request.user.id, followers=context['news'].author.id).exists()
        comment = self.get_page_comment()
        context['page_comment'] = comment
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
    context = {'news': news, 'ais': ais, 'len_comments': len_comments, 'comments': comments, 'comments_sub': comments_sub, 'news_only_author': news_only_author, 'form': form}
    return render(request, 'news_output/news_detail.html', context)



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
        context['search_text'] = self.request.GET.get('query')
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


class Profile(ListView, DetailView):
    template_name = 'news_output/profile_info.html'
    model = AdvUser
    paginate_by = 2
    # slug_url_kwarg = 'slug'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_detail'] = AdvUser.objects.get(pk=context['object'].pk)
        context['auth'] = 0
        context['data'] = context['object_list']
        context['type_data'] = self.kwargs['section']
        context['followers_count'] = Follow.objects.filter(followers=context['user_detail'].pk).exclude(user_id=context['user_detail']).count()
        context['following_count'] = Follow.objects.filter(user_id=context['user_detail']).exclude(followers=context['user_detail'].pk).count()
        return context

    def get_object(self, queryset=None):
        pk = (AdvUser.objects.get(slug=self.kwargs['slug'])).pk
        return pk

    # def get(self, request, **kwargs):
        # user = AdvUser.objects.get(slug=self.kwargs['slug'])
        # if self.kwargs['section'] == 'news':
        # self.object = self.get_object(queryset=AdvUser.objects.get(slug=self.kwargs['slug']))
        # elif self.kwargs['section'] == 'comment':
        #     self.object = self.get_object(queryset=Comment.objects.filter(author=user.id))
        # elif self.kwargs['section'] == 'favourites_posts':
        #     return None
        # else:
        #     print('hfg')
        # # self.object = self.get_object(queryset=)
        # return super().get(request, **kwargs)

    def get_queryset(self, **kwargs):
        self.object = AdvUser.objects.get(username=self.kwargs['slug'])
        if self.kwargs['section'] == 'news':
            return self.object.news_set.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1, likedislike__target_comment=None)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1, likedislike__target_comment=None))).order_by('-published')
        elif self.kwargs['section'] == 'comment':
            return self.object.comment_set.annotate(like=Count('likedislike', filter=Q(likedislike__is_like=1)), dislike=Count('likedislike', filter=Q(likedislike__is_dislike=1))).order_by('-created_at')
        elif self.kwargs['section'] == 'following':
            return self.object.following_set.filter(user_id=self.object).exclude(followers=self.object.pk)
        elif self.kwargs['section'] == 'followers':
            return self.object.followers_set.filter(followers=self.object.pk).exclude(user_id=self.object)
        elif self.kwargs['section'] == 'favourites_posts':
            return None
        else:
            return super().get_queryset(**kwargs)

@csrf_exempt
def AjaxSubscription(request):
    resp = HttpResponse("", content_type='text/plain; charset=utf- 8', status=200)
    if request.method == 'POST' and request.POST['author_id'] != request.POST['user_id']:
            user = AdvUser.objects.get(id=request.POST['user_id'])
            subcribe = Follow.objects.filter(user_id=user, followers=request.POST['author_id'])
            if not subcribe.exists():
                follow = Follow()
                follow.user_id = user
                follow.followers = request.POST['author_id']
                follow.save()
                resp.write('Вы подписаны')
            else:
                subcribe.delete()
                resp.write('Вы отписались')
            # except Follow.DoesNotExist:
    else:
        resp.write('Вы не можете подписаться на самого себя')
    return resp
