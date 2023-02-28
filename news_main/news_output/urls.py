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
    path('detail/<int:pk>/', NewsDetailView.as_view(), kwargs={'only_comment': False}, name='detail'),
    path('detail/<int:pk>/comment/', NewsDetailView.as_view(), kwargs={'only_comment': True}, name='detail_all_comment'),
    path('search/', SearchNews.as_view(), kwargs={'type_sort': 'default'}, name='search'),
    path('search/<str:type_sort>/', SearchNews.as_view(), name='search_sort'),
    path('my_publication/<str:type_sort>/<int:user_id>/', PublicationUser.as_view(), name='publication_user_auth'),
    path('users/put_like_dislike/', AjaxLikeDislike, name='put_like_dislike'),
    path('users/<slug:slug>/', Profile.as_view(), kwargs={'section': 'main'}, name='users_info'),
    path('users/<slug:slug>/<str:section>/', Profile.as_view(), name='users_info_section'),
    path('users/subcription', AjaxSubscription, name='subscription')
]