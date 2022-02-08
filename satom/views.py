from django.shortcuts import render
from satom.models import Challenge
from django.db.models import Count
from users.models import Profile
from satom.forms import GuessForm
from django.contrib.auth.decorators import login_required
import time


answer_list = [] # mot ***** -> lettres révélées
attempts = [] # liste des différents essais
nb_try = 0
colors = {"correct": "#00A000", "partial": "#FF9600", "false": "#000000"}
#emoji = {"correct": "🟥", "partial": "🟨", "false":"🟦"}
emoji = {"correct": "🟩", "partial": "🟨", "false":"⬛"}
state = "guess" # guess/win/lose
attempts_emoji = "" # version affichée sur le site
emoji_clipboard = "" # version collée dans le presse-papiers


def to_emoji(tries, nb_try, challenge, time, user):
    str_emoji = ""
    clipboard = "SATOM N°" + str(challenge) + " - " + str(user) +"\\n\\n"
    for i in range(nb_try):
        for j in range(len(tries[i])):
            str_emoji = str_emoji + emoji[tries[i][j]["value"]]
            clipboard = clipboard + emoji[tries[i][j]["value"]]
        str_emoji = str_emoji + "\n"
        clipboard = clipboard + "\\n"

    if nb_try == 1:
        clipboard = clipboard + "\\nRéussi en 1 coup et en " + time + " ! OMG"
    else:
        clipboard = clipboard + "\\nRéussi en " + str(nb_try) + " coups  et en " + time + "!"
    print(str_emoji)
    return str_emoji, clipboard

def calcul_temps(started, ended):
    temps = ""
    diff = int(ended - started)
    if diff / 3600 >= 1:
        temps = "+ d'1 heure tu es nul"
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
    return [temps, diff]

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

def motus(guess, word, a_list):

    longueur = len(word)
    word_list = list(word)
    guess_list = list(guess)
    result_list = ["false"] * longueur

    for i in range(longueur):
        if guess_list[i] == word_list[i]:
            result_list[i] = "correct"
            a_list[i] = guess[i]

            guess_list[i] = "+"
            word_list[i] = "-"

    for i in range(longueur):
        for j in range(len(word)):
            if guess_list[i] == word_list[j]:
                result_list[i] = "partial"

                guess_list[i] = "+"
                word_list[j] = "-"

    return result_list, a_list

@login_required()
def home(request):
    buttons = []
    challenges = Challenge.objects.all().order_by('id')
    for chall in challenges:
        if chall in request.user.profile.completedChall.all():
            buttons.append([chall.pk, "done"])
        else:
            buttons.append([chall.pk, "nodone"])

    context = {
        "challenges": challenges,
        "buttons": buttons,
    }
    return render(request, 'home.html', context)

@login_required()
def challenge(request, pk):
    session = request.session

    global attempts_emoji
    global emoji_clipboard

    curr_challenge = Challenge.objects.get(pk=pk)
    chall_id = "challenge" + str(pk)
    word = curr_challenge.word
    longueur = len(word)
    form = GuessForm(longueur)

    completed = False



    if request.GET.get('guess'):
        if session[chall_id]['nb_try'] < 6 and session[chall_id]['state'] == "guess":

            session[chall_id]['guess'] = str(request.GET.get('guess')).lower()
            session[chall_id]['result'], session[chall_id]['answer_list'] = motus(session[chall_id]['guess'], word, session[chall_id]['answer_list'])

            session[chall_id]['guess_list'] = list(session[chall_id]['guess'].upper())

            for i in range(longueur):
                session[chall_id]['attempts'][session[chall_id]['nb_try']][i]["letter"] = session[chall_id]['guess_list'][i]
                session[chall_id]['attempts'][session[chall_id]['nb_try']][i]["value"] = session[chall_id]['result'][i]
                session[chall_id]['attempts'][session[chall_id]['nb_try']][i]["color"] = colors[session[chall_id]['result'][i]]

            session[chall_id]['nb_try'] += 1

            if session[chall_id]['guess'].lower() == word.lower():
                # GG
                session[chall_id]['state'] = "win"
                session[chall_id]['ended'] = time.time()
                session[chall_id]['time_spent'] = calcul_temps(session[chall_id]['started'], session[chall_id]['ended'])

                session[chall_id]['attempts_emoji'], session[chall_id]['emoji_clipboard'] = to_emoji(session[chall_id]['attempts'], session[chall_id]['nb_try'], pk, session[chall_id]['time_spent'][0], request.user)

                request.user.profile.completedChall.add(curr_challenge)
                request.user.profile.challenges.append([pk, session[chall_id]['time_spent'], session[chall_id]['nb_try']])
                request.user.profile.save()

            elif session[chall_id]['nb_try'] < 6:
                for j in range(longueur):
                    if session[chall_id]['answer_list'][j] != '*':
                        session[chall_id]['attempts'][session[chall_id]['nb_try']][j]["letter"] = session[chall_id]['answer_list'][j].upper()
                        session[chall_id]['attempts'][session[chall_id]['nb_try']][j]["value"] = "correct"
                        session[chall_id]['attempts'][session[chall_id]['nb_try']][j]["color"] = colors["correct"]
            else:
                # FF
                session[chall_id]['state'] = "lose"

    elif not (chall_id in session.keys()):

        session[chall_id] = {}
        session[chall_id]['nb_try'] = 0
        session[chall_id]['answer_list'] = ["*"] * longueur
        session[chall_id]['attempts'] = []
        session[chall_id]['state'] = "guess"
        session[chall_id]['attempts_emoji'] = ""
        session[chall_id]['emoji_clipboard'] = ""
        session[chall_id]['started'] = time.time()
        session[chall_id]['time_spent'] = ["", 0]

        for i in range(6):
            session[chall_id]['attempt'] = []
            for j in range(longueur):
                session[chall_id]['attempt'].append({"letter": "*", "value": "false", "color": colors["false"]})
            session[chall_id]['attempts'].append(session[chall_id]['attempt'])

        session[chall_id]['answer_list'][0] = word[0]
        session[chall_id]['attempts'][nb_try][0]["letter"] = session[chall_id]['answer_list'][0].upper()
        session[chall_id]['attempts'][nb_try][0]["value"] = "correct"
        session[chall_id]['attempts'][nb_try][0]["color"] = colors["correct"]


    if curr_challenge in request.user.profile.completedChall.all() and session[chall_id]["state"] == "guess":
        completed = True
        session[chall_id]['answer_list'] = word.split()
        attempt = []
        for j in range(longueur):
            attempt.append({"letter": word[j].upper(), "value": "correct", "color": colors["correct"]})
        session[chall_id]['attempts'][0] = attempt

    else:
        completed = False

    context = {
        "challenge": curr_challenge,
        "form": form,
        "longueur": longueur,
        "answer": "".join(session[chall_id]['answer_list']),
        "attempts": session[chall_id]['attempts'],
        "state": session[chall_id]['state'],
        "emoji": session[chall_id]['attempts_emoji'],
        "clipboard": session[chall_id]['emoji_clipboard'],
        "time_spent": session[chall_id]['time_spent'][0],
        "completed": completed,
    }
    return render(request, 'challenge.html', context)

def classement(request):
    scores = []
    users = Profile.objects.all().annotate(score=Count('completedChall')).order_by('-score')

    for user in users:
        words = user.challenges
        time_list = []
        try_list = []
        for word in words:
            time_list.append(word[1][1])
            try_list.append(word[2])
        avg_time = calcul_stats(time_list)
        avg_try = calcul_stats(try_list)

        scores.append([user, user.score, avg_try, avg_time])
    context = {
        "users": scores,
    }
    return render(request, 'classement.html', context)