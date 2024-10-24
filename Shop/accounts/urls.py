from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('verify/register/', views.UserRegisterVerifyCodeView.as_view(), name='register_verify_code'),
    path('verify/login/', views.UserLoginVerifyCodeView.as_view(), name='login_verify_code'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

]