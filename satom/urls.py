from django.urls import path, include
from satom import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm
from .views import register

urlpatterns = [
    path('', views.home, name='home'),
    path("<int:pk>/", views.challenge, name="challenge"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("classement/", views.classement, name="classement"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html", authentication_form=CustomAuthenticationForm), name="login"),
    path("register/", register, name="register"),
]
