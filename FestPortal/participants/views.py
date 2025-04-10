# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CompleteProfileForm

#Partcipant views
@login_required
def complete_profile(request):
    user = request.user

    #Prevent organizers from accessing this view
    if user.is_organizer:
            return redirect('organizer_dashboard')

    # If profile is already completed, redirect
    if all([user.name, user.gender, user.dob, user.mobile, user.college]):
        return redirect('participant_dashboard')

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('participant_dashboard')
    else:
        form = CompleteProfileForm(instance=user)

    return render(request, 'participants/complete_profile.html', {'form': form})

from .models import TeamMembership
@login_required
def participant_dashboard(request):
    user = request.user
    if user.is_organizer:
        messages.warning(request, "Organizers are not allowed on the participant dashboard.")
        return redirect('organizer_dashboard')
    user = request.user
    college_mates = User.objects.filter(college=user.college, is_organizer=False).exclude(id=user.id)

    memberships = TeamMembership.objects.filter(participant=user).select_related('team__event')
    events_joined = [m.team.event for m in memberships]

    return render(request, 'participants/participant_dashboard.html', {
        'user': user,
        'events_joined': events_joined,
        'college_mates': college_mates,
        }
    )

from django.contrib import messages
from .models import Event, Team, TeamMembership

@login_required
def join_event(request):
    user = request.user

    # Get events user is not already in
    joined_event_ids = TeamMembership.objects.filter(participant=user).values_list('team__event_id', flat=True)
    available_events = Event.objects.exclude(id__in=joined_event_ids).filter(
        gender__in=[user.gender, 'Mixed']
    )

    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
            return redirect('join_event')

        # Gender check
        if event.gender != 'Mixed' and user.gender != event.gender:
            messages.error(request, "You're not eligible for this event.")
            return redirect('join_event')

        # Get or create the team
        team, created = Team.objects.get_or_create(event=event, college=user.college)

        # Check if team is full
        if TeamMembership.objects.filter(team=team).count() >= event.max_team_size:
            messages.error(request, "Team is already full.")
            return redirect('join_event')

        # Add to team
        TeamMembership.objects.create(team=team, participant=user)
        messages.success(request, f"You've joined {event.sport.name} - {event.gender}")
        return redirect('participant_dashboard')

    return render(request, 'participants/join_event.html', {
        'available_events': available_events,
    })

@login_required
def view_my_team(request, event_id):
    user = request.user

    try:
        event = Event.objects.get(id=event_id)
        team = Team.objects.get(event=event, college=user.college)
    except (Event.DoesNotExist, Team.DoesNotExist):
        messages.error(request, "Team not found.")
        return redirect('participant_dashboard')

    members = TeamMembership.objects.filter(team=team).select_related('participant')

    return render(request, 'participants/my_team.html', {
        'event': event,
        'members': members,
    })

from .models import Match, TeamMembership

@login_required
def participant_schedule(request):
    user = request.user
    if user.is_organizer:
        messages.warning(request, "Organizers can't view participant schedule.")
        return redirect('organizer_dashboard')

    # Matches the user is personally in (via their team or as individual)
    my_team_ids = TeamMembership.objects.filter(participant=user).values_list('team_id', flat=True)
    my_events = Match.objects.filter(
        Q(team1__in=my_team_ids) |
        Q(team2__in=my_team_ids) |
        Q(teams__in=my_team_ids) |
        Q(individuals=user)
    ).distinct().filter(start_time__gte=now()).order_by('start_time')

    # Other matches where the college is participating
    college_matches = Match.objects.filter(
        Q(team1__college=user.college) |
        Q(team2__college=user.college) |
        Q(teams__college=user.college)
    ).exclude(id__in=my_events.values_list('id', flat=True)).distinct().filter(start_time__gte=now()).order_by('start_time')

    return render(request, 'participants/participant_schedule.html', {
        'my_events': my_events,
        'college_matches': college_matches,
    })


#Organiser Views
from django.db.models import Count
from .models import User, College

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps
from django.conf import settings

def organizer_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_organizer:
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@organizer_required
def organizer_dashboard(request):
    participants = User.objects.filter(is_organizer=False).select_related('college')
    colleges = College.objects.annotate(num_participants=Count('user'))

    return render(request, 'participants/organizer_dashboard.html', {
        'participants': participants,
        'colleges': colleges,
        'total_participants': participants.count(),
        'total_colleges': colleges.filter(num_participants__gt=0).count(),
    }
)

@organizer_required
def college_participants(request, college_id):
    college = College.objects.get(pk=college_id)
    participants = User.objects.filter(college=college)

    return render(request, 'participants/college_participants.html', {
        'college': college,
        'participants': participants,
    }
)


@organizer_required
def organizer_teams(request):
    teams = Team.objects.select_related('event', 'college')

    # Optional filters from GET query
    sport = request.GET.get('sport')
    gender = request.GET.get('gender')
    college = request.GET.get('college')

    if sport:
        teams = teams.filter(event__sport__name__icontains=sport)
    if gender:
        teams = teams.filter(event__gender__icontains=gender)
    if college:
        teams = teams.filter(college__name__icontains=college)

    return render(request, 'participants/organizer_teams.html', {'teams': teams})


@organizer_required
def team_players(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    members = TeamMembership.objects.filter(team=team).select_related('participant')
    return render(request, 'participants/team_players.html', {'team': team, 'members': members})


@organizer_required
def college_events(request, college_id):
    college = get_object_or_404(College, pk=college_id)
    teams = Team.objects.filter(college=college).select_related('event')
    return render(request, 'participants/college_events.html', {'college': college, 'teams': teams})


#Matches Views
from .models import Match
from django.db.models import Q
from django.utils.timezone import now

@organizer_required
def match_list(request):
    matches = Match.objects.select_related('event', 'team1__college', 'team2__college')

    # Filters via query params
    sport = request.GET.get('sport')
    gender = request.GET.get('gender')
    college = request.GET.get('college')
    status = request.GET.get('status')

    if sport:
        matches = matches.filter(event__sport__name__icontains=sport)
    if gender:
        matches = matches.filter(event__gender__icontains=gender)
    if college:
        matches = matches.filter(Q(team1__college__name__icontains=college) | Q(team2__college__name__icontains=college))
    if status:
        matches = matches.filter(status=status)

    return render(request, 'participants/match_list.html', {'matches': matches})


@organizer_required
def match_detail(request, match_id):
    match = Match.objects.select_related('event', 'team1__college', 'team2__college').get(pk=match_id)
    team1_players = TeamMembership.objects.filter(team=match.team1).select_related('participant')
    team2_players = TeamMembership.objects.filter(team=match.team2).select_related('participant')

    return render(request, 'participants/match_detail.html', {
        'match': match,
        'team1_players': team1_players,
        'team2_players': team2_players
    })

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Match, Event, Team, User
from django.contrib.auth.decorators import login_required

@organizer_required
def upload_matches_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                event = Event.objects.get(sport__name=row['Sport'], gender=row['Gender'])
                match = Match.objects.create(
                    event=event,
                    format=row['Format'],
                    start_time=row['Start Time'],
                    end_time=row['End Time'],
                    location=row.get('Location', ''),
                    status=row['Status'],
                )

                # Assign teams or individuals
                if match.format == 'teamvsteam':
                    match.team1 = Team.objects.get(id=row['Team1 ID'])
                    match.team2 = Team.objects.get(id=row['Team2 ID'])
                    match.save()
                elif match.format == 'team_multi':
                    match.teams.set(Team.objects.filter(id__in=[int(i) for i in str(row['Teams']).split(',')]))
                elif match.format in ['individualvindividual', 'individual_multi']:
                    match.individuals.set(User.objects.filter(id__in=[int(i) for i in str(row['Participants']).split(',')]))

            messages.success(request, "Matches uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

        return redirect('match_list')

    return render(request, 'participants/upload_matches.html')

#Scorekeeping


from .forms import MatchResultForm

@organizer_required
def update_match_result(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, "Match result updated successfully.")
            return redirect('match_detail', match_id=match.id)
    else:
        form = MatchResultForm(instance=match)

    return render(request, 'participants/update_match_result.html', {
        'form': form,
        'match': match
    })

@organizer_required
def match_results(request):
    matches = Match.objects.filter(status='Completed').select_related('event', 'team1__college', 'team2__college')

    sport = request.GET.get('sport')
    if sport:
        matches = matches.filter(event__sport__name__icontains=sport)

    return render(request, 'participants/match_results.html', {'matches': matches})

from .models import Match, TeamMembership, Team
from django.db.models import Q

@login_required
def participant_match_results(request):
    user = request.user
    if user.is_organizer:
        return redirect('organizer_dashboard')

    # Get all teams user is part of
    team_ids = TeamMembership.objects.filter(participant=user).values_list('team_id', flat=True)

    # Matches where the participant was involved or their college had a team
    matches = Match.objects.filter(
        Q(status='Completed'),
        Q(team1__in=team_ids) | Q(team2__in=team_ids) |
        Q(teams__college=user.college) | Q(team1__college=user.college) | Q(team2__college=user.college)
    ).distinct().select_related('event', 'team1__college', 'team2__college')

    return render(request, 'participants/participant_match_results.html', {
        'matches': matches
    })

@organizer_required
def update_match_result(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            match.status = 'Completed'
            match.save()
            messages.success(request, "Result updated successfully.")
            return redirect('match_detail', match_id=match.id)
    else:
        form = MatchResultForm(instance=match)

    return render(request, 'participants/match_result.html', {'form': form, 'match': match})
