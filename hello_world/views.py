from django.shortcuts import render
from satom.models import Challenge

def hello_world(request):
    daily_chall = Challenge.objects.all().latest('pk')
    daily_pk = daily_chall.pk
    context = {
        "daily": daily_pk,
    }
    return render(request, 'hello_world.html', context)
