from django.db import models
from django.contrib.auth.models import User
import string, random
# Create your models here.
class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.title}"
    def question_list(self):
        return self.questions.all()
class Question(models.Model): 
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    answer = models.TextField()
    allow_multiple_answers = models.BooleanField(default=False)

    def __str__(self):
        return self.text
class FlashcardSet(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.title}"
    def flashcard_list(self):
        return self.flashcards.all()
class Flashcard(models.Model): 
    FlashcardSet = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='flashcards')
    front = models.TextField()
    back = models.TextField()
    def __str__(self):
        return self.front
def genCode():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=6))

class GuessWhoGame(models.Model):
    code = models.CharField(max_length=6, default=genCode, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')
    opponent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='joined_games')
    chosen_character = models.CharField(max_length = 100, null=True, blank=True)
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    def is_full(self):
        return self.creator is not None and self.opponent is not None
    
    def __str__(self):
        return f"Game {self.code}"

