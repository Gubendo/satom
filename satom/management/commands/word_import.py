from django.core.management.base import BaseCommand, CommandError
from satom.models import MotPossible
import os

class Command(BaseCommand):
    help = "Importe tous les mots depuis un fichier texte avec le format mot;difficulte"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="mots.txt",
            help="Chemin vers le fichier de mots (défaut : mots.txt dans le dossier du projet)"
        )

    def handle(self, *args, **options):
        filepath = options['file']
        if not os.path.exists(filepath):
            raise CommandError(f"Le fichier {filepath} n'existe pas.")

        total = 0
        creates = 0

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or ";" not in line:
                    self.stdout.write(self.style.WARNING(f"Ligne ignorée : '{line}'"))
                    continue

                mot, difficulte = line.split(";")
                mot = mot.lower().strip()

                obj, created = MotPossible.objects.get_or_create(
                    mot=mot,
                    defaults={"difficulte": int(difficulte)}
                )

                total += 1
                creates += int(created)
        
        self.stdout.write(self.style.SUCCESS(f"Import terminé !"))
        self.stdout.write(f"- Lignes lues : {total}")
        self.stdout.write(f"- Nouveaux mots ajoutés : {creates}")
        self.stdout.write(f"- Mots déjà existants : {total - creates}")