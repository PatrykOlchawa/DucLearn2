from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils.html import strip_tags
from .models import Test, Question, FlashcardSet, Flashcard, GuessWhoGame
from .forms import TestForm, QuestionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})

def tests(request):
    alltests = Test.objects.filter(user=request.user)
    template = loader.get_template('all_tests.html')
    context = {
        'alltests': alltests,
        }
    return HttpResponse(template.render(context, request))
def test_details(request, id):
    mytest = Test.objects.get(id=id)
    questions = mytest.question_list().values()
    template = loader.get_template('test_details.html')
    context = {
            'mytest' : mytest,
            'questions' : questions,
            }
    return HttpResponse(template.render(context, request))
def solve_test(request, id, questionId):
    mytest = Test.objects.get(id=id)
    questions = mytest.question_list()
    #if(questionId == -1):
    #    qustion = questions.get.
   # print(f"{len(questions)}")
    
    #if index > len(questions): 
    #    return redirect('test_finished', id=id)
    if not any(q.id == questionId for q in questions):
        return redirect('test_finished', id=id)

    question = questions.get(id=questionId)
    question_index = [q.id for q in questions].index(question.id) + 1
    if 'answers' not in request.session:
        request.session['answers'] = {}

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        answers = request.session['answers']
        answers[str(questionId)] = selected_answer  # use str keys for JSON serializability
        request.session['answers'] = answers
    template = loader.get_template('solve_test.html')
    context = {
            'mytest' : mytest,
            'question' : question,
            'question_id' : questionId,
            'num_questions' : len(questions), 
            'index' : question_index
            }
    return HttpResponse(template.render(context, request))
def start_test(request, id):
    request.session['answers'] = {} 
    mytest = Test.objects.get(id=id)
    firstId = mytest.question_list().first().id
    if not firstId:
        return HttpResponse("No questions in this test.")
    template = loader.get_template('solve_test_initial.html')
    context = {
            'mytest' : mytest,
            'firstId' : firstId
            }
    return HttpResponse(template.render(context, request))
def test_finished(request, id):
    test = Test.objects.get(id=id)
    questions = list(test.question_list())
    answers = request.session.get('answers', {})
    score = 0
    for index, question in enumerate(questions):
        user_answer = answers.get(str(question.id))
        if user_answer == question.answer:
            score += 1
#       print(f"User answer {user_answer}") 
#       print(f"Correct answer {question.answer}")
    template = loader.get_template('test_finished.html')
    context = {
            'final_score' : score, 
            }
    return HttpResponse(template.render(context, request))
def add_test(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TestForm(request.POST)
            if form.is_valid():
                test = form.save(commit=False)
                test.user = request.user
                test.save()
                return redirect('details', test.id)
        else:
            form = TestForm()
        return render(request, 'add_test.html', {'form':form})
def add_questions(request, id):
    test = Test.objects.get(id=id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            return redirect('add_questions', id=test.id)
    else:
        form = QuestionForm()
    return render(request, 'add_questions.html', {'form':form, 'test':test})
def delete_test(request, id):
    test = Test.objects.get(id=id)
    test.delete()
    return render(render, 'all_tests.html')
@login_required
def flashcards(request):
    flashcards = FlashcardSet.objects.filter(user=request.user)
    return render(request, 'flashcards.html', {'flashcards':flashcards})
@login_required
def flashcardSet(request, setId):
    flashcardSet = FlashcardSet.objects.get(id=setId)
#    flashcards = flashcardSet.flashcard_list()
 #   flashcard = flashcards.objects.get(id=flashcardID)
    return render(request, 'flashcard.html', {'flashcardSet':flashcardSet})
def get_flashcard(request, setId, cardId):
    flashcardSet = FlashcardSet.objects.get(id=setId)
    flashcards = list(flashcardSet.flashcard_list())
    if 0 <= cardId < len(flashcards):
       card = flashcards[cardId]
       return JsonResponse({
        'index': cardId,
        'front': card.front,
        'back': card.back,
        'total': len(flashcards),
        }) 
    return JsonResponse({'error':'Out of range'}, status=404)

def guess_who(request): 
    return render(request, 'guess_who.html')
def create_game(request):
    game = GuessWhoGame.objects.create(creator=request.user)
    return redirect('choose_character', game_code=game.code)
def join_game(request):
    if request.method == "POST":
        code = request.POST.get("code").upper()
        try:
            game = GuessWhoGame.objects.get(code=code)
        except GuessWhoGame.DoesNotExist:
            return render(request, "join_game.html", {"error": "Game not found!"})
        if game.is_full():
            return render(request, "join_game.html", {"error": "Game full"})
            
        game.opponent = request.user
        game.save()
        
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"guesswho_{code}",
            {
                "type": "game_message",
                "data": {
                    "type": "player_joined",
                    "username": request.user.username
                }
            }
        )
        if game.is_full():
            async_to_sync(layer.group_send)(
                f"guesswho_{code}",
                {
                    "type": "game_message",
                    "data": { "type": "start_game" }
                }
            )

        return redirect("waiting_room", game_code=code)
        
    return render(request, "join_game.html")
def choose_character(request, game_code):
    game = GuessWhoGame.objects.get(code=game_code)
    if request.method == "POST":
        game.chosen_character = request.POST.get("character")
        game.save()
        return redirect('waiting_room', game_code=game_code)
    return render(request, "choose_character.html", {"game":game})

def guess_game(request, game_code):
    game = GuessWhoGame.objects.get(code=game_code)
    return render(request, "guess_game.html", {"game":game})

def waiting_room(request, game_code):
    game = GuessWhoGame.objects.get(code=game_code)
    return render(request, "waiting_room.html", {"game":game})

