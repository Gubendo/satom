from datetime import datetime, date
from django.http import Http404
from enclose.game.loader import load_puzzle
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import EnclosePuzzle, PuzzleScore
from django.http import JsonResponse
from django.db.models import Sum


@login_required
def enclose_view(request):
    today = date.today()

    requested_date = request.GET.get("date")

    if requested_date:
        try:
            d = datetime.strptime(requested_date, "%Y-%m-%d").date()
        except ValueError:
            raise Http404("Date invalide")
        
        puzzle = EnclosePuzzle.objects.filter(date=d).first()
        
        if puzzle is None:
            puzzle = (
            EnclosePuzzle.objects
            .filter(date__lte=date.today())
            .order_by("-date")
            .first()
        )
    else:
        # puzzle du jour ou dernier
        puzzle = (
            EnclosePuzzle.objects
            .filter(date__lte=date.today())
            .order_by("-date")
            .first()
        )
    user_score = None
    if request.user.is_authenticated:
        user_score = (
            PuzzleScore.objects
            .filter(user=request.user, puzzle=puzzle)
            .first()
        )

    # Classement global du puzzle
    leaderboard = (
        PuzzleScore.objects
        .filter(puzzle=puzzle)
        .select_related("user")
        .order_by("-area", "walls_used", "created_at")
    )

    first_finisher = (
    PuzzleScore.objects
    .filter(puzzle=puzzle)
    .order_by("created_at")
    .first()
    )
    first_finisher_user_id = first_finisher.user_id if first_finisher else None

    leaderboard_data = [
        {
            "username": s.user.username,
            "area": s.area,
            "walls": s.walls_used,
            "me": s.user_id == request.user.id,
            "first_finisher": (s.user_id == first_finisher_user_id),
        }
        for s in leaderboard
    ]

    leaderboard = leaderboard[:10]

    

    context = {
        "puzzle_json": json.dumps({
            "id": puzzle.puzzle_id,
            "date": str(puzzle.date),
            "size": puzzle.size,
            "max_walls": puzzle.max_walls,
            "grid": puzzle.grid,
        }),
        "locked": bool(user_score),
        "saved_walls": user_score.walls if user_score else [],
        "puzzle_date": puzzle.date,
        "leaderboard_json": json.dumps(leaderboard_data),
        "user_score": user_score,
    }

    return render(
        request,
        "enclose/enclose.html",
        context
    )

@csrf_exempt
@login_required
def submit_score(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = json.loads(request.body)
    puzzle = EnclosePuzzle.objects.get(puzzle_id=data["puzzle_id"])

    print("hello")
    PuzzleScore.objects.update_or_create(
        user=request.user,
        puzzle=puzzle,
        defaults={
            "area": data["area"],
            "walls": data["walls"],
            "walls_used": len(data["walls"])
        },
    )

    rank = (
        PuzzleScore.objects
        .filter(puzzle=puzzle, area__gt=data["area"])
        .count() + 1
    )

    leaderboard = (
        PuzzleScore.objects
        .filter(puzzle=puzzle)
        .select_related("user")
        .order_by("-area", "walls_used", "created_at")
    )

    first_finisher = (
    PuzzleScore.objects
    .filter(puzzle=puzzle)
    .order_by("created_at")
    .first()
    )
    first_finisher_user_id = first_finisher.user_id if first_finisher else None

    leaderboard_data = [
        {
            "username": s.user.username,
            "area": s.area,
            "walls": s.walls_used,
            "me": s.user_id == request.user.id,
            "first_finisher": (s.user_id == first_finisher_user_id),
        }
        for s in leaderboard
    ]

    leaderboard = leaderboard[:10]

    return JsonResponse({
        "rank": rank,
        "leaderboard_json": json.dumps(leaderboard_data)
        })

def daily_leaderboard(request):
    puzzle = EnclosePuzzle.objects.get(date=date.today())

    scores = (
        PuzzleScore.objects
        .filter(puzzle=puzzle)
        .select_related("user")
        .order_by("-area", "created_at")
    )

    return render(
        request,
        "daily_enclose/leaderboard.html",
        {"scores": scores}
    )


def global_leaderboard(request):
    leaderboard = (
        PuzzleScore.objects
        .values("user__username")
        .annotate(total_area=Sum("area"))
        .order_by("-total_area")
    )

    return render(
        request,
        "daily_enclose/global_leaderboard.html",
        {"leaderboard": leaderboard}
    )

def user_history(request):
    history = (
        PuzzleScore.objects
        .filter(user=request.user)
        .select_related("puzzle")
        .order_by("-puzzle__date")
    )

    return render(
        request,
        "daily_enclose/history.html",
        {"history": history}
    )

