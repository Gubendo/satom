from django.urls import path
from satom import views

urlpatterns = [
    path('', views.home, name='home'),
    path("<int:pk>/", views.challenge, name="challenge"),
]
