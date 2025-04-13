from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class College(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):

    gender_choices = [
        ('Men', 'Men'),
        ('Women', 'Women'),
    ]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=5, choices=gender_choices, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    is_organizer = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)
    profile_complete = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username

    def is_profile_complete(self):
        required_fields = [self.name, self.gender, self.dob, self.mobile, self.college]
        return all(required_fields)


# Events

class Sport(models.Model):
    name = models.CharField(max_length=100)

class Event(models.Model):
    GENDER_CHOICES = [('Men', 'Men'), ('Women', 'Women'), ('Mixed', 'Mixed')]

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    max_team_size = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.sport.name} - {self.gender}"

class Team(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='captained_teams')

    def __str__(self):
        return f"{self.college.name} - {self.event}"

class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


#Matches

from django.db import models
from django.core.exceptions import ValidationError
from .models import Event, Team, User

class Match(models.Model):
    FORMAT_CHOICES = [
        ('teamvsteam', 'Team vs Team'),
        ('individualvindividual', 'Individual vs Individual'),
        ('team_multi', 'Multiple Teams'),
        ('individual_multi', 'Multiple Individuals'),
    ]

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
    ]

    RESULT_CHOICES = [
        ('Team 1 Won', 'Team 1 Won'),
        ('Team 2 Won', 'Team 2 Won'),
        ('Draw', 'Draw'),
        ('Tied', 'Tied'),
        ('Cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    format = models.CharField(max_length=30, choices=FORMAT_CHOICES, default='teamvsteam')

    # For team-based matches
    team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='team2_matches')

    # For multi-team or individual events
    teams = models.ManyToManyField(Team, blank=True)
    individuals = models.ManyToManyField(User, blank=True)

    # Timing and location
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True)

    # Status and outcome
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, null=True, blank=True)
    team1_score = models.CharField(max_length=50, null=True, blank=True)
    team2_score = models.CharField(max_length=50, null=True, blank=True)
    result_notes = models.TextField(blank=True, null=True)

    def clean(self):
        if self.format == 'teamvsteam' and (not self.team1 or not self.team2):
            raise ValidationError("Team vs Team match must have exactly 2 teams.")
        if self.format == 'individualvindividual' and self.individuals.count() != 2:
            raise ValidationError("Individual vs Individual match must have exactly 2 participants.")
        if self.format == 'team_multi' and self.teams.count() < 2:
            raise ValidationError("Multi-team match must have at least 2 teams.")
        if self.format == 'individual_multi' and self.individuals.count() < 2:
            raise ValidationError("Multi-individual match must have at least 2 participants.")

    def __str__(self):
        return f"{self.event.sport.name} | {self.get_format_display()} | {self.start_time.strftime('%Y-%m-%d %H:%M')}"

#Feedback system
# models.py

class Feedback(models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_organizer': False})
    message = models.TextField()
    image = models.ImageField(upload_to='feedback_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.participant.name or self.participant.email}"

#LeaderBoard


class Leaderboard(models.Model):
    name = models.CharField(max_length=100)  # 'Overall', 'Football', etc.
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    is_overall = models.BooleanField(default=False)
    uploaded_excel = models.FileField(upload_to='leaderboards/excels/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()

    class Meta:
        ordering = ['rank']
