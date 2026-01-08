from django.urls import path
from .views import puzzle_api, submit_api, list_puzzles

urlpatterns = [
    path("puzzle/", puzzle_api),
    path("puzzles/", list_puzzles, name="list_puzzles"),
    path("submit/", submit_api),
]