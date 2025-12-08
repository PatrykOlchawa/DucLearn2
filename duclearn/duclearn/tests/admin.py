from django.contrib import admin
from .models import Test, Question, FlashcardSet, Flashcard, GuessWhoGame
from .models import Question
# Register your models here.
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(FlashcardSet)
admin.site.register(Flashcard)
admin.site.register(GuessWhoGame)
