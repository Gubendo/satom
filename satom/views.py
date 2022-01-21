from django.shortcuts import render
from satom.models import Challenge
from satom.forms import GuessForm

answer_list = [] # mot ***** -> lettres révélées
attempts = [] # liste des différents essais
nb_try = 0
colors = {"correct": (255,0,0), "partial": (255,255,0), "false": (0,0,0)}
emoji = {"correct": "🟥", "partial": "🟡", "false":"🟦"}
state = "guess" # guess/win/lose
attempts_emoji = "" # version affichée sur le site
emoji_clipboard = "" # version collée dans le presse-papiers

def to_emoji(tries, nb_try, challenge):
    str_emoji = ""
    clipboard = "SATOM N°" + str(challenge) + "\\n\\n"
    for i in range(nb_try):
        for j in range(len(tries[i])):
            str_emoji = str_emoji + emoji[tries[i][j]["value"]]
            clipboard = clipboard + emoji[tries[i][j]["value"]]
        str_emoji = str_emoji + "\n"
        clipboard = clipboard + "\\n"

    if nb_try == 1:
        clipboard = clipboard + "\\nRéussi en 1 coup ! OMG"
    else:
        clipboard = clipboard + "\\nRéussi en " + str(nb_try) + " coups !"
    print(str_emoji)
    return str_emoji, clipboard

def motus(guess, word):
    global answer_list

    longueur = len(word)
    word_list = list(word)
    guess_list = list(guess)
    result_list = ["false"] * longueur

    for i in range(longueur):
        if guess_list[i] == word_list[i]:
            result_list[i] = "correct"
            answer_list[i] = guess[i]

            guess_list[i] = "+"
            word_list[i] = "-"

    for i in range(longueur):
        for j in range(len(word)):
            if guess_list[i] == word_list[j]:
                result_list[i] = "partial"

                guess_list[i] = "+"
                word_list[j] = "-"

    return result_list

def home(request):
    challenges = Challenge.objects.all().order_by('id')
    context = {
        "challenges": challenges,
    }
    return render(request, 'home.html', context)

def challenge(request, pk):
    global answer_list
    global attempts
    global nb_try
    global state
    global attempts_emoji
    global emoji_clipboard

    curr_challenge = Challenge.objects.get(pk=pk)
    word = curr_challenge.word
    longueur = len(word)
    form = GuessForm(longueur)
    if request.GET.get('guess'):
        if nb_try < 6 and state == "guess":

            guess = str(request.GET.get('guess')).lower()
            result = motus(guess, word)

            guess_list = list(guess.upper())
            for i in range(longueur):
                attempts[nb_try][i]["letter"] = guess_list[i]
                attempts[nb_try][i]["value"] = result[i]
                attempts[nb_try][i]["color"] = colors[result[i]]

            nb_try += 1

            if guess.lower() == word.lower():
                print("GG")
                state = "win"
                attempts_emoji, emoji_clipboard = to_emoji(attempts, nb_try, pk)

            elif nb_try < 6:
                for j in range(longueur):
                    if answer_list[j] != '*':
                        attempts[nb_try][j]["letter"] = answer_list[j].upper()
                        attempts[nb_try][j]["value"] = "correct"
                        attempts[nb_try][j]["color"] = colors["correct"]
            else:
                print("perdu")
                state = "lose"

        else:
            print("TRY MAX")

    else:
        nb_try = 0
        answer_list = ["*"] * longueur
        attempts = []
        state = "guess"
        attempts_emoji = ""
        emoji_clipboard = ""

        for i in range(6):
            attempt = []
            for j in range(longueur):
                attempt.append({"letter": "*", "value": "false", "color": colors["false"]})
            attempts.append(attempt)

    context = {
        "challenge": curr_challenge,
        "form": form,
        "longueur": longueur,
        "answer": "".join(answer_list),
        "attempts": attempts,
        "state": state,
        "emoji": attempts_emoji,
        "clipboard": emoji_clipboard,
    }
    return render(request, 'challenge.html', context)


