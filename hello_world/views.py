from django.shortcuts import render
from satom.models import Challenge
from users.models import Roi

def hello_world(request):
    daily_chall = Challenge.objects.all().latest('pk')
    daily_pk = daily_chall.pk

    king = Roi.objects.all().latest('pk')
    context = {
        "daily": daily_pk,
        "roi": king,
    }
    return render(request, 'hello_world.html', context)
