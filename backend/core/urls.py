from django.urls import path
from .views import (
    ActiveElectionView, LatestElectionView, CandidateList, results_view, token_login, cast_vote, FraudReportCreate,
    admin_elections, admin_active_election, admin_candidate_create, admin_candidate_detail, debug_date, admin_import_voters, admin_send_tokens, admin_voter_stats, api_root
)

urlpatterns = [
    # API root
    path('', api_root, name='api-root'),
    
    # publik
    path('elections/active/', ActiveElectionView.as_view()),
    path('elections/latest/', LatestElectionView.as_view()),
    path('candidates/', CandidateList.as_view()),
    path('results/', results_view),
    path('auth/token-login/', token_login),
    path('vote/', cast_vote),
    path('reports/', FraudReportCreate.as_view()),

    # admin (KPU)
    path('admin/elections/', admin_elections),                 # GET list, POST create
    path('admin/election/active/', admin_active_election),     # GET/PUT active (atau ?id=)
    path('admin/candidates/', admin_candidate_create),         # POST create
    path('admin/candidates/<int:pk>/', admin_candidate_detail),
    path('admin/voters/import/', admin_import_voters),
    path('admin/voters/send-tokens/', admin_send_tokens),
    path('admin/voters/stats/', admin_voter_stats),

    path('debug/date/', debug_date),
]
