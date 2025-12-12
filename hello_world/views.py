from django.shortcuts import render
from satom.models import Challenge, MotPossible
import random
from datetime import date
from users.models import Roi


def calcul_temps(diff):
    temps = ""
    if diff / 3600 >= 1:
        temps = "+ d'1 heure"
    elif diff / 60 >= 1:
        minute = diff // 60
        sec = diff % 60
        if minute == 1:
            minstr = " minute"
        else:
            minstr = " minutes"

        if sec == 1:
            secstr = " seconde"
        else:
            secstr = " secondes"
        temps = str(minute) + minstr + " et " + str(sec) + secstr

    else:
        temps = str(diff) + " secondes"
    return temps

def hello_world(request):
    daily_chall = Challenge.objects.all().latest('number')
    daily_pk = daily_chall.number

    daily_word = Challenge.objects.filter(date=date.today()).first()
    if not daily_word:
        words = MotPossible.objects.filter(
            used=False,
            longueur__gte=5,
            longueur__lte=7,
            difficulte__lte=3
        )
        chosen_word = words.order_by('?').first()
        if chosen_word:
            chosen_word.used = True
            chosen_word.save()
            chosen_word = Challenge.objects.create(
                word=chosen_word.mot,
                number = daily_chall.number + 1
            )
            daily_pk = chosen_word.number
    

    king = Roi.objects.all().latest('pk')
    time = calcul_temps(king.time)
    context = {
        "daily": daily_pk,
        "roi": king,
        "time": time,
    }
    return render(request, 'hello_world.html', context)


def rules(request):
    context = {
        
    }
    return render(request, 'rules.html', context)