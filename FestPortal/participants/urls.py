from django.urls import path, include
from .views import complete_profile
from .views import (organizer_dashboard, college_participants,
                    participant_dashboard,join_event,
                    view_my_team, organizer_teams,
                    team_players, college_events,
                    match_list,match_detail,upload_matches_excel,
                    participant_schedule,update_match_result,
                    match_results,participant_match_results
                    )

urlpatterns = [


    path('accounts/', include('allauth.urls')),
    path('complete-profile/', complete_profile, name='complete_profile'),
    path('dashboard/', participant_dashboard, name='participant_dashboard'),
    path('my-team/<int:event_id>/', view_my_team, name='view_my_team'),
    path('join-event/', join_event, name='join_event'),
    path('participant/schedule/', participant_schedule, name='participant_schedule'),
    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('organizer/college/<int:college_id>/participants/', college_participants, name='college_participants'),
    path('organizer/teams/', organizer_teams, name='organizer_teams'),
    path('organizer/team/<int:team_id>/players/', team_players, name='team_players'),
    path('organizer/college/<int:college_id>/events/', college_events, name='college_events'),
    path('organizer/matches/', match_list, name='match_list'),
    path('organizer/matches/<int:match_id>/', match_detail, name='match_detail'),
    path('organizer/upload-matches/', upload_matches_excel, name='upload_matches'),
    path('organizer/match/<int:match_id>/update/', update_match_result, name='update_match_result'),
    path('organizer/match-results/', match_results, name='match_results'),
    path('participant/results/', participant_match_results, name='participant_match_results'),

]
