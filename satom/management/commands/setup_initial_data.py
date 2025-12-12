import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from satom.models import MotPossible, Challenge
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = "Initial setup: superuser, import mots.txt, create first Challenge"

    def handle(self, *args, **options):
        self.create_superuser()
        self.import_mots()
        self.create_initial_challenge()
        self.create_initial_king()
        self.stdout.write(self.style.SUCCESS("✅ Initial data setup completed."))

    def create_superuser(self):
        if not User.objects.filter(is_superuser=True).exists():
            username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write("Superuser already exists, skipping.")

    def import_mots(self):
        mots_file = os.path.join(os.getcwd(), "mots.txt")
        if not os.path.exists(mots_file):
            self.stdout.write(self.style.WARNING(f"mots.txt not found at {mots_file}, skipping import."))
            return

        count = 0
        with open(mots_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # La ligne peut contenir le mot et éventuellement sa difficulté, séparés par une virgule
                parts = line.split(";")
                mot = parts[0].strip().lower()
                difficulte = parts[1].strip() if len(parts) > 1 else "1"
                # Evite les doublons
                if not MotPossible.objects.filter(mot=mot).exists():
                    MotPossible.objects.create(mot=mot, difficulte=difficulte)
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} mots imported into MotPossible."))

    def create_initial_challenge(self):
        if Challenge.objects.exists():
            self.stdout.write("Challenge already exists, skipping creation.")
            return

        mot_list = MotPossible.objects.all()
        if not mot_list.exists():
            self.stdout.write(self.style.WARNING("No MotPossible available, cannot create initial Challenge."))
            return

        mot = random.choice(mot_list)
        Challenge.objects.create(
            word=mot,
            number=0,
            date=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f"Initial Challenge created with word '{mot.mot}'."))
