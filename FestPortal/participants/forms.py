from django import forms
from .models import User

class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'gender', 'dob', 'mobile', 'college']
        widgets = {
                    'dob': forms.DateInput(attrs={'type': 'date'}),
                }


from .models import Match, Team, User
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class MatchCreateForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'event', 'format', 'team1', 'team2', 'teams', 'individuals',
            'start_time', 'end_time', 'location'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'teams': forms.CheckboxSelectMultiple(),
            'individuals': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team1'].queryset = Team.objects.all()
        self.fields['team2'].queryset = Team.objects.all()
        self.fields['teams'].queryset = Team.objects.all()
        self.fields['individuals'].queryset = User.objects.filter(is_organizer=False)
        self.fields['team1'].required = False
        self.fields['team2'].required = False
        self.fields['teams'].required = False
        self.fields['individuals'].required = False


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score', 'result', 'status']


from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your feedback...'}),
        }


from .models import Match

class MatchScoreForm(forms.ModelForm):
    team1_score = forms.CharField(required=False)
    team2_score = forms.CharField(required=False)
    result = forms.ChoiceField(choices=Match.RESULT_CHOICES, required=False)
    result_notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score', 'result', 'result_notes']

    def __init__(self, *args, **kwargs):
        self.sport = kwargs.pop('sport', None)
        super().__init__(*args, **kwargs)

        if self.sport == 'Cricket':
            self.fields['team1_score'].label = 'Team 1 Score (e.g. 120/8)'
            self.fields['team2_score'].label = 'Team 2 Score (e.g. 118 all out)'
        elif self.sport == 'Football':
            self.fields['team1_score'].label = 'Goals by Team 1'
            self.fields['team2_score'].label = 'Goals by Team 2'
        elif self.sport in ['Athletics', 'Swimming']:
            self.fields['result_notes'].label = 'Ranks / Status (e.g. Player A: Rank 1, Qualified)'
            del self.fields['team1_score']
            del self.fields['team2_score']
            del self.fields['result']

from django import forms
from .models import Leaderboard, LeaderboardEntry

class LeaderboardForm(forms.ModelForm):
    class Meta:
        model = Leaderboard
        fields = ['name', 'event', 'is_overall', 'uploaded_excel']

class LeaderboardEntryForm(forms.ModelForm):
    class Meta:
        model = LeaderboardEntry
        fields = ['college', 'points', 'rank']
