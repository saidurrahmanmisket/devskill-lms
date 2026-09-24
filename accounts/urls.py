from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_redirect_view, name='role_redirect'),
    path('demo-login/<str:role>/', views.demo_login_view, name='demo_login'),
    path('demo/<str:role>/', views.demo_login_view, name='demo_login_alias'),
]
