from django.urls import path
from .views import enclose_view, submit_score, daily_leaderboard, user_history

urlpatterns = [
    path("", enclose_view, name="enclose"),
    path("submit/", submit_score, name="submit_score"),
    path("leaderboard/", daily_leaderboard, name="enclose_leaderboard"),
    path("history/", user_history, name="enclose_history"),
    


]