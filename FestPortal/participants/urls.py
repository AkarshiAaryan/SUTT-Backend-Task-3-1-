from os import remove

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from .views import (organizer_dashboard, college_participants,
                    participant_dashboard,join_event,
                    view_my_team, organizer_teams,
                    team_players, college_events,
                    match_list,match_detail,upload_matches_excel,
                    participant_schedule,update_match_result,
                    match_results,participant_match_results,home,give_feedback,view_feedbacks,create_match,
                    complete_profile, remove_player, ban_player, create_leaderboard,view_leaderboard,
                    add_entry, all_leaderboards, set_team_captain, approve_requests
                    )

urlpatterns = [

    path('', home, name='home'),
    path('accounts/', lambda request: redirect('account_login')),
    path('accounts/', include('allauth.urls')),

    path('complete-profile/', complete_profile, name='complete_profile'),
    path('dashboard/', participant_dashboard, name='participant_dashboard'),
    path('my-team/<int:event_id>/', view_my_team, name='view_my_team'),
    path('join-events/', join_event, name='join_events'),
    path('participant/schedule/', participant_schedule, name='participant_schedule'),
    path('feedback/', give_feedback, name='give_feedback'),
    path('participant/results/', participant_match_results, name='participant_match_results'),

    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('organizer/college/<int:college_id>/participants/', college_participants, name='college_participants'),
    path('organizer/teams/', organizer_teams, name='organizer_teams'),
    path('organizer/team/<int:team_id>/players/', team_players, name='team_players'),
    path('organizer/college/<int:college_id>/events/', college_events, name='college_events'),
    path('organizer/matches/create/', create_match, name='create_match'),
    path('organizer/matches/', match_list, name='match_list'),
    path('organizer/matches/<int:match_id>/', match_detail, name='match_detail'),
    path('organizer/upload-matches/', upload_matches_excel, name='upload_matches'),
    path('organizer/match/<int:match_id>/update/', update_match_result, name='update_match_result'),
    path('organizer/match-results/', match_results, name='match_results'),
    path('organizer/feedbacks/', view_feedbacks, name='view_feedbacks'),
    path('organizer/remove-player/<int:user_id>/<int:event_id>/', remove_player, name='remove_player'),
    path('organizer/ban-player/<int:user_id>/', ban_player, name='ban_player'),

    path('leaderboards/create/', create_leaderboard, name='create_leaderboard'),
    path('leaderboards/<int:leaderboard_id>/', view_leaderboard, name='view_leaderboard'),
    path('leaderboards/<int:leaderboard_id>/add-entry/', add_entry, name='add_entry'),
    path('leaderboards/', all_leaderboards, name='all_leaderboards'),


    path('organizer/team/<int:team_id>/set-captain/', set_team_captain, name='set_team_captain'),


    path('captain/approve-requests/', approve_requests, name='approve_requests'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
