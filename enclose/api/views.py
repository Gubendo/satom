from datetime import date
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from enclose.game.validator import validate_solution
from django.contrib.auth.decorators import login_required
from enclose.models import EnclosePuzzle, PuzzleScore


def puzzle_api(request):
    puzzle = generate_puzzle(date.today())
    return JsonResponse(puzzle)

@require_POST
def submit_api(request):
    data = json.loads(request.body)
    walls = {tuple(map(tuple, w)) for w in data["walls"]}

    puzzle = generate_puzzle(date.today())
    valid, score = validate_solution(puzzle, walls)

    return JsonResponse({
        "valid": valid,
        "score": score,
    })

@login_required
def list_puzzles(request):
    user = request.user
    current_date = request.GET.get("current_date")

    puzzles = (
        EnclosePuzzle.objects
        .order_by("-date")
    )

    result = []
    for p in puzzles:
        locked = PuzzleScore.objects.filter(user=user, puzzle=p).exists()
        is_current = (str(p.date) == current_date)

        result.append({
            "name" : p.puzzle_id,
            "id": p.id,
            "date": str(p.date),
            "formatted_date": str(p.date.strftime("%d/%m/%Y")),
            "locked": locked,
            "current": is_current,
        })

    return JsonResponse(result, safe=False)