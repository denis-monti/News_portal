from django.urls import path, include
from django.contrib.auth.views import *
from rest_framework import routers


from .views import *

app_name = 'news_output'

urlpatterns = [
    path('index/', NewsIndexView.as_view(), kwargs={'type_sort': 'default'}, name='index'),
    path('index/<str:type_sort>/', NewsIndexView.as_view(), name='index_sort'),
    # path('ajax_sorting/', ajax_sorting, name='ajax_sorting'),
    path('<int:rubric_id>/', NewsByRubricView.as_view(), kwargs={'type_sort': 'default'}, name='by_rubric'),
    path('edit_news/<int:pk>/', NewsEditView.as_view(), name='edit_news'),
    path('delete_news/<int:pk>/', NewsDeleteView.as_view(), name='delete_news'),
    path('<int:rubric_id>/<str:type_sort>/', NewsByRubricView.as_view(), name='by_rubric'),
    path('add/', NewsCreateView.as_view(), name='news_add'),
    path('detail/<int:pk>/', NewsDetailView.as_view(), name='detail'),
    path('search/', SearchNews.as_view(), kwargs={'type_sort': 'default'}, name='search'),
    path('search/<str:type_sort>/', SearchNews.as_view(), name='search_sort'),
    path('my_publication/<str:type_sort>/<int:user_id>/', PublicationUser.as_view(), name='publication_user_auth'),
    path('', AjaxLikeDislike, name='put_like_dislike')
]