from django.urls import path
from django.contrib.auth.views import *



from .views import *

app_name = 'news_auth'

urlpatterns = [
    path('accounts/login/', Login.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='news_output:index', template_name="news_output/logout.html"), name='logout'),
    path('accounts/password_change/', PasswordChange.as_view(), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(template_name="news_auth/change_password_done.html", extra_context={'auth': 0}), name='password_change_done'),
    path('accounts/password_reset/', PasswordResetSend.as_view(), name='password_reset'),
    path('accounts/password_reset/done', PasswordResetDoneView.as_view(template_name='news_auth/email_sent.html', extra_context={'auth': 0}),  name='password_reset_done'),
    path('accounts/reset/<uid64>/<token>/', PasswordResetConfirmView.as_view(template_name='news_auth/confirm_password.html', extra_context={'auth': 0}), name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(template_name="news_auth/password_confirmed.html", extra_context={'auth': 0}), name='password_reset_complete'),

]