from django.shortcuts import render
from satom.models import Challenge
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
    daily_chall = Challenge.objects.all().latest('pk')
    daily_pk = daily_chall.pk

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