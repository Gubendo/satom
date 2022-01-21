from django.urls import path, include
from users import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('account/', include("django.contrib.auth.urls")),
    path('register/', views.register, name="register")
]