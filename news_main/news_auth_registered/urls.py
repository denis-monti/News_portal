from django.urls import path
from django.contrib.auth.views import *





from .views import *

app_name = 'news_auth_registered'

urlpatterns = [
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', Login.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='news_output:index', template_name="news_output/logout.html"), name='logout'),
    path('accounts/password_change/', PasswordChange.as_view(), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(template_name="news_auth_registered/change_password_done.html", extra_context={'auth': 0}), name='password_change_done'),
    path('accounts/password_reset/', PasswordResetSend.as_view(), name='password_reset'),
    path('accounts/password_reset/done', PasswordResetDoneView.as_view(template_name='news_auth_registered/email_sent.html', extra_context={'auth': 0}),  name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='news_auth_registered/password_reset_confirm.html', extra_context={'auth': 0}, success_url=reverse_lazy("news_auth_registered:password_reset_complete")), name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(template_name="news_auth_registered/password_confirmed.html", extra_context={'auth': 0}), name='password_reset_complete'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/setting/', ProfileSetting.as_view(), name='profile_setting'),
]