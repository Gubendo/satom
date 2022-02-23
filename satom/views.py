from django.shortcuts import render
from satom.models import Challenge
from django.db.models import Count
from users.models import Profile, Roi
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
    return str_emoji, clipboard

def calcul_temps(started, ended):
    temps = ""
    diff = int(ended - started)
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

def updateKing(king, chall_id, timeS):
    if chall_id > king.challengeID:
        return True
    if chall_id == king.challengeID and timeS < king.time:
        return True
    return False

def motus(guess, word, a_list, lettres):

    longueur = len(word)
    word_list = list(word)
    guess_list = list(guess)
    result_list = ["false"] * longueur


    for i in range(longueur):
        if guess_list[i] == word_list[i]:
            result_list[i] = "correct"
            a_list[i] = guess[i]

            # couleur verte pour lettres[i] == guess_list[i]
            for row in lettres:
                for lettre in row:
                    if lettre['letter'].lower() == guess_list[i]:
                        lettre['color'] = "#00A000"

            guess_list[i] = "+"
            word_list[i] = "-"

    for i in range(longueur):
        for j in range(len(word)):
            if guess_list[i] == word_list[j]:
                result_list[i] = "partial"

                # couleur jaune pour lettres[i] == guess_list[i]
                for row in lettres:
                    for lettre in row:
                        if lettre['letter'].lower() == guess_list[i] and lettre['color'] != "#00A000":
                            lettre['color'] = "#FF9600"

                guess_list[i] = "+"
                word_list[j] = "-"

    for i in range(longueur):
        if guess_list[i] != "+":
            # couleur rouge pour lettres[i] = guess_list[i]
            for row in lettres:
                for lettre in row:
                    if lettre['letter'].lower() == guess_list[i] and lettre['color'] != "#00A000" and lettre['color'] != "#FF9600":
                        lettre['color'] = "#B1B1B1"

    return result_list, a_list, lettres

@login_required()
def home(request):
    buttons = []
    challenges = Challenge.objects.all().order_by('id')
    unite = 0
    dizaine = -1
    for chall in challenges:
        if unite % 8 == 0:
            dizaine +=1
            buttons.append([])
            unite = 1
        if chall in request.user.profile.completedChall.all():
            buttons[dizaine].append([chall.pk, "done"])
        else:
            buttons[dizaine].append([chall.pk, "nodone"])

        unite += 1

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
    daily_challenge = Challenge.objects.all().latest('pk')
    if curr_challenge == daily_challenge:
        lastWord = True
    else:
        lastWord = False

    chall_id = "challenge" + str(pk)
    word = curr_challenge.word
    longueur = len(word)
    form = GuessForm(longueur)

    completed = False


    if request.GET.get('guess'):
        if session[chall_id]['nb_try'] < 6 and session[chall_id]['state'] == "guess":

            session[chall_id]['guess'] = str(request.GET.get('guess')).lower()
            session[chall_id]['result'], session[chall_id]['answer_list'], session[chall_id]['lettres'] = motus(session[chall_id]['guess'], word, session[chall_id]['answer_list'], session[chall_id]['lettres'])

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

                current_king = Roi.objects.all().latest('pk')
                new_king = updateKing(current_king, pk, session[chall_id]['time_spent'][1])
                if new_king :
                    current_king.king = request.user.profile
                    current_king.challengeID = pk
                    current_king.time = session[chall_id]['time_spent'][1]
                    current_king.tries = session[chall_id]['nb_try']
                    current_king.save()


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
        session[chall_id]['lettres'] = [[{"letter":'A', "color": "#000000"}, {"letter":'Z', "color": "#000000"}, {"letter":'E', "color": "#000000"}, {"letter":'R', "color": "#000000"}, {"letter":'T', "color": "#000000"}, {"letter":'Y', "color": "#000000"}, {"letter":'U', "color": "#000000"}, {"letter":'I', "color": "#000000"}, {"letter":'O', "color": "#000000"}, {"letter":'P', "color": "#000000"}],
                                        [{"letter":'Q', "color": "#000000"}, {"letter":'S', "color": "#000000"}, {"letter":'D', "color": "#000000"}, {"letter":'F', "color": "#000000"}, {"letter":'G', "color": "#000000"}, {"letter":'H', "color": "#000000"}, {"letter":'J', "color": "#000000"}, {"letter":'K', "color": "#000000"}, {"letter":'L', "color": "#000000"}, {"letter":'M', "color": "#000000"}],
                                        [{"letter":'W', "color": "#000000"}, {"letter":'X', "color": "#000000"}, {"letter":'C', "color": "#000000"}, {"letter":'V', "color": "#000000"}, {"letter":'B', "color": "#000000"}, {"letter":'N', "color": "#000000"}]]

        for i in range(6):
            session[chall_id]['attempt'] = []
            for j in range(longueur):
                session[chall_id]['attempt'].append({"letter": "*", "value": "false", "color": colors["false"]})
            session[chall_id]['attempts'].append(session[chall_id]['attempt'])

        session[chall_id]['answer_list'][0] = word[0]
        session[chall_id]['attempts'][nb_try][0]["letter"] = session[chall_id]['answer_list'][0].upper()
        session[chall_id]['attempts'][nb_try][0]["value"] = "correct"
        session[chall_id]['attempts'][nb_try][0]["color"] = colors["correct"]

    elif not ('lettres' in session[chall_id].keys()):
        session[chall_id]['lettres'] = [[{"letter": 'A', "color": "#000000"}, {"letter": 'Z', "color": "#000000"},
                                         {"letter": 'E', "color": "#000000"}, {"letter": 'R', "color": "#000000"},
                                         {"letter": 'T', "color": "#000000"}, {"letter": 'Y', "color": "#000000"},
                                         {"letter": 'U', "color": "#000000"}, {"letter": 'I', "color": "#000000"},
                                         {"letter": 'O', "color": "#000000"}, {"letter": 'P', "color": "#000000"}],
                                        [{"letter": 'Q', "color": "#000000"}, {"letter": 'S', "color": "#000000"},
                                         {"letter": 'D', "color": "#000000"}, {"letter": 'F', "color": "#000000"},
                                         {"letter": 'G', "color": "#000000"}, {"letter": 'H', "color": "#000000"},
                                         {"letter": 'J', "color": "#000000"}, {"letter": 'K', "color": "#000000"},
                                         {"letter": 'L', "color": "#000000"}, {"letter": 'M', "color": "#000000"}],
                                        [{"letter": 'W', "color": "#000000"}, {"letter": 'X', "color": "#000000"},
                                         {"letter": 'C', "color": "#000000"}, {"letter": 'V', "color": "#000000"},
                                         {"letter": 'B', "color": "#000000"}, {"letter": 'N', "color": "#000000"}]]

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
        "alreadyCompleted": completed,
        "lastWord": lastWord,
        "lettresDispo": session[chall_id]['lettres']
    }
    return render(request, 'challenge.html', context)


def get_note(users):
    return users.get('note')

def classement(request):
    scores = []
    notes = []
    users = Profile.objects.all().annotate(score=Count('completedChall')).order_by('-score')
    rank = 1

    for user in users:
        words = user.challenges
        time_list = []
        try_list = []
        for word in words:
            time_list.append(word[1][1])
            try_list.append(word[2])

        avg_time = calcul_stats(time_list)
        avg_try = calcul_stats(try_list)

        if avg_time != 0 and avg_try != 0:
            grade_time = (20 - ((avg_time - 60) * 20 / 840)) * 3
            if grade_time <=0: grade_time = 0
            grade_tries = (20 - ((avg_try - 1) * 20 / 6)) * 2
        else:
            grade_time = 0
            grade_tries = 0

        avg_grade = (grade_time + grade_tries) / 5
        notes.append({'name': user, 'note': avg_grade + 20*user.score, 'time': avg_time, 'tries': avg_try})

    notes.sort(key=get_note, reverse=True)

    for note in notes:
        user = note['name']
        avg_try = note['tries']
        avg_time = note['time']

        if rank == 1:
            name = "🏆 " + str(user)
        elif rank == 2:
            name = "🥈 " + str(user)
        elif rank == 3:
            name = "🥉 " + str(user)
        else:
            name = "" + str(rank) + " - " + str(user)

        scores.append([name, user.score, avg_try, avg_time])
        rank+=1

    context = {
        "users": scores,
    }
    return render(request, 'classement.html', context)
