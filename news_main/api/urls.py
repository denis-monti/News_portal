from django.urls import path

from .views import *

app_name = 'api'

urlpatterns = [
    path('news/<int:pk>/comments/', comments),
    path('news/<int:pk>', NewsDetailView.as_view()),
    path('news/', news),
    path('rubrics/<int:pk>/', api_rubric_detail),
    path('rubrics/', api_rubrics),
]