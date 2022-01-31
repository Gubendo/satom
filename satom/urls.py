from django.urls import path, include
from satom import views

urlpatterns = [
    path('', views.home, name='home'),
    path("<int:pk>/", views.challenge, name="challenge"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("classement/", views.classement, name="classement")
]
