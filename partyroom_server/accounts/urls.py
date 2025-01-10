from django.conf.urls import include
from django.urls import path, re_path
from knox import views as knox_views
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.AccountOTPView, basename='otp')
router.register("", views.UserForgotPasswordView, basename='')


urlpatterns = [
    path('register/', views.CustomUserCreateView.as_view({'post': 'create'}), name='user_register'),
    path('user/', views.CustomUserDetailView.as_view(), name='user_detail'),
    path('favourite/', views.UserfavouriteView.as_view({'get': 'retrieve', 'put': 'put', 'delete': 'destroy'}), name='user_favourite'),
    path('change_password/', views.CustomUserChangePasswordView.as_view(), name='user_change_password'),
    path('login/', views.LoginView.as_view(), name='knox_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('remove_account/<str:uid>', views.CustomUserDestoryView.as_view(), name='user_remove'),
    path('', include(router.urls))
]
