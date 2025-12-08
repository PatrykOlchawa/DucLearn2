from django import forms
from .models import Test,Question

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description']
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'answer']
