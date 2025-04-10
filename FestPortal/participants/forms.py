from django import forms
from .models import User

class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'gender', 'dob', 'mobile', 'college']
        widgets = {
                    'dob': forms.DateInput(attrs={'type': 'date'}),
                }

from .models import Match

class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score', 'result', 'status']
