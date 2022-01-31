from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def calcul_stats(full_list):
    total = 0
    long = len(full_list)
    if long == 0:
        avg = 0
    else:
        for i in range(long):
            total += full_list[i]

        avg = total / long
    return round(avg, 2)

def dashboard(request):
    user = request.user
    avg_time = 0
    avg_try = 0
    if user.is_authenticated:
        words = user.profile.challenges
        time_list = []
        try_list = []
        for word in words:
            time_list.append(word[1][1])
            try_list.append(word[2])
        avg_time = calcul_stats(time_list)
        avg_try = calcul_stats(try_list)

    else:
        words = []


    context = {
        "words": words,
        "avg_time": avg_time,
        "avg_try": avg_try,
    }
    return render(request, "users/dashboard.html", context)

def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": UserCreationForm}
        )
    elif request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))
