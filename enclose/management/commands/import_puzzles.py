import json
from pathlib import Path
from django.core.management.base import BaseCommand
from enclose.models import EnclosePuzzle
from datetime import date

class Command(BaseCommand):
    help = "Importe les puzzles JSON tels quels dans la base"

    def handle(self, *args, **options):
        puzzles_dir = Path(__file__).resolve().parents[3] / "enclose" / "puzzles"

        for path in puzzles_dir.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))

            EnclosePuzzle.objects.update_or_create(
                puzzle_id=data["puzzle_id"],
                defaults={
                    "date": date.fromisoformat(data["date"]),
                    "size": data["size"],
                    "max_walls": data["max_walls"],
                    "grid": data["grid"],
                },
            )

            self.stdout.write(f"{data['puzzle_id']} importé")
