from django.urls import path, include
from hello_world import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("rules/", views.rules, name='rules')

]
