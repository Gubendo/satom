from django.shortcuts import render
from satom.models import Challenge
from satom.forms import GuessForm
from django.contrib.auth.decorators import login_required
import time


answer_list = [] # mot ***** -> lettres révélées
attempts = [] # liste des différents essais
nb_try = 0
#colors = {"correct": (255,0,0), "partial": (255,150,0), "false": (0,0,0)}
colors = {"correct": (0,160,0), "partial": (255,150,0), "false": (0,0,0)}
#emoji = {"correct": "🟥", "partial": "🟨", "false":"🟦"}
emoji = {"correct": "🟩", "partial": "🟨", "false":"⬛"}
state = "guess" # guess/win/lose
attempts_emoji = "" # version affichée sur le site
emoji_clipboard = "" # version collée dans le presse-papiers

def to_emoji(tries, nb_try, challenge, time):
    str_emoji = ""
    clipboard = "SATOM N°" + str(challenge) + "\\n\\n"
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
    return temps


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

def home(request):
    buttons = []
    challenges = Challenge.objects.all().order_by('id')
    for chall in challenges:
        if request.user in chall.completed.all():
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
    print(curr_challenge)
    print(curr_challenge.completed.all())
    word = curr_challenge.word
    longueur = len(word)
    form = GuessForm(longueur)

    if request.GET.get('guess'):
        if session['nb_try'] < 6 and session['state'] == "guess":

            session['guess'] = str(request.GET.get('guess')).lower()
            session['result'], session['answer_list'] = motus(session['guess'], word, session['answer_list'])

            session['guess_list'] = list(session['guess'].upper())

            for i in range(longueur):
                session['attempts'][session['nb_try']][i]["letter"] = session['guess_list'][i]
                session['attempts'][session['nb_try']][i]["value"] = session['result'][i]
                session['attempts'][session['nb_try']][i]["color"] = colors[session['result'][i]]

            session['nb_try'] += 1

            if session['guess'].lower() == word.lower():
                # GG
                session['state'] = "win"
                session['ended'] = time.time()
                session['time_spent'] = calcul_temps(session['started'], session['ended'])

                session['attempts_emoji'], session['emoji_clipboard'] = to_emoji(session['attempts'], session['nb_try'], pk, session['time_spent'])
                curr_challenge.completed.add(request.user)
                curr_challenge.save()

            elif session['nb_try'] < 6:
                for j in range(longueur):
                    if session['answer_list'][j] != '*':
                        session['attempts'][session['nb_try']][j]["letter"] = session['answer_list'][j].upper()
                        session['attempts'][session['nb_try']][j]["value"] = "correct"
                        session['attempts'][session['nb_try']][j]["color"] = colors["correct"]
            else:
                # FF
                session['state'] = "lose"

    else:
        session['nb_try'] = 0
        session['answer_list'] = ["*"] * longueur
        session['attempts'] = []
        session['state'] = "guess"
        session['attempts_emoji'] = ""
        session['emoji_clipboard'] = ""
        session['started'] = time.time()
        session['time_spent'] = ""

        for i in range(6):
            session['attempt'] = []
            for j in range(longueur):
                session['attempt'].append({"letter": "*", "value": "false", "color": colors["false"]})
            session['attempts'].append(session['attempt'])

        session['answer_list'][0] = word[0]
        session['attempts'][nb_try][0]["letter"] = session['answer_list'][0].upper()
        session['attempts'][nb_try][0]["value"] = "correct"
        session['attempts'][nb_try][0]["color"] = colors["correct"]

    context = {
        "challenge": curr_challenge,
        "form": form,
        "longueur": longueur,
        "answer": "".join(session['answer_list']),
        "attempts": session['attempts'],
        "state": session['state'],
        "emoji": session['attempts_emoji'],
        "clipboard": session['emoji_clipboard'],
        "time_spent": session['time_spent'],
    }
    return render(request, 'challenge.html', context)


