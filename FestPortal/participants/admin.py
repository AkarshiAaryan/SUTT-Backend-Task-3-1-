from django.contrib import admin
from .models import User, College, Sport,TeamMembership,Team,Event
from .models import Leaderboard, LeaderboardEntry
# Register your models here.

admin.site.register(User)
admin.site.register(College)
admin.site.register(Sport)
admin.site.register(Event)
admin.site.register(Team)
admin.site.register(TeamMembership)

admin.site.register(Leaderboard)
admin.site.register(LeaderboardEntry)

from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('event', 'team1', 'team2', 'start_time', 'end_time', 'status')
    list_filter = ('event__sport', 'event__gender', 'status', 'team1__college', 'team2__college')



