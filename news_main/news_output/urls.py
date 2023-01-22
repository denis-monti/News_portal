from django.urls import path, include
from django.contrib.auth.views import *
from rest_framework import routers


from .views import *

app_name = 'news_output'

urlpatterns = [
<<<<<<< HEAD
    path('api/rubrics/<int:pk>/', api_rubric_detail),
    path('api/rubrics/', api_rubrics),
=======
>>>>>>> e2147defc2401c88eeef7eac9411b5da21982db5
    path('index/', NewsIndexView.as_view(), kwargs={'type_sort': 'default'}, name='index'),
    path('index/<str:type_sort>/', NewsIndexView.as_view(), name='index_sort'),
    # path('ajax_sorting/', ajax_sorting, name='ajax_sorting'),
    path('<int:rubric_id>/', NewsByRubricView.as_view(), kwargs={'type_sort': 'default'}, name='by_rubric'),
    path('update_news/<int:pk>/', NewsEditView.as_view(), name='edit_news'),
    path('<int:rubric_id>/<str:type_sort>/', NewsByRubricView.as_view(), name='by_rubric'),
    path('add/', NewsCreateView.as_view(), name='news_add'),
    path('detail/<int:pk>/', NewsDetailView.as_view(), name='detail'),
    path('search/', SearchNews.as_view(), kwargs={'type_sort': 'default'}, name='search'),
    path('search/<str:type_sort>/', SearchNews.as_view(), name='search_sort')
]