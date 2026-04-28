from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Student
    path('student/submit/', views.student_submit, name='student_submit'),
    path('student/analyse/', views.student_analyse, name='student_analyse'),
    path('student/analysis/<int:doc_id>/', views.student_analysis, name='student_analysis'),
    path('student/approve-edit/', views.approve_edit, name='approve_edit'),
    path('student/version/<int:doc_id>/', views.student_version_history, name='student_version'),
    path('student/dashboard/<int:doc_id>/', views.student_dashboard, name='student_dashboard'),
    path('student/howto/', views.howto, name='howto'),
    path('student/docs/', views.student_docs, name='student_docs'),

    # Teacher
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/stats/', views.teacher_stats, name='teacher_stats'),
    path('teacher/student/<int:student_id>/', views.teacher_student, name='teacher_student'),
    path('teacher/rubric/', views.teacher_rubric, name='teacher_rubric'),
    path('teacher/rubric/save/', views.teacher_rubric_save, name='teacher_rubric_save'),
    path('teacher/rubric/delete/<int:pk>/', views.teacher_rubric_delete, name='teacher_rubric_delete'),
    path('teacher/upload/', views.teacher_upload, name='teacher_upload'),
    path('teacher/feedback/', views.teacher_class_feedback, name='teacher_feedback'),

    # Peer Review
    path('peer/feed/', views.peer_feed, name='peer_feed'),
    path('peer/review/<int:share_id>/', views.peer_review, name='peer_review'),
    path('peer/share/<int:doc_id>/', views.share_section, name='share_section'),
    path('peer/close/<int:share_id>/', views.close_share, name='close_share'),
    path('peer/activity/', views.my_peer_activity, name='peer_activity'),
    path('peer/edit/<int:feedback_id>/', views.edit_peer_feedback, name='edit_peer_feedback'),
    path('peer/delete/<int:feedback_id>/', views.delete_peer_feedback, name='delete_peer_feedback'),

    # Teacher comments
    path('teacher/comment/<int:doc_id>/', views.add_teacher_comment, name='add_teacher_comment'),
    path('teacher/comment/delete/<int:comment_id>/', views.delete_teacher_comment, name='delete_teacher_comment'),
    path('teacher/peer-overview/', views.teacher_peer_overview, name='teacher_peer_overview'),
    path('teacher/reports/', views.teacher_review_reports, name='teacher_review_reports'),
    path('teacher/report/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),

    # User settings & preferences
    path('settings/', views.user_settings, name='user_settings'),

    # Feedback reporting
    path('feedback/<int:feedback_id>/flag/', views.flag_feedback, name='flag_feedback'),

    # Revision + download
    path('student/revise/<int:doc_id>/', views.save_revision, name='save_revision'),
    path('student/download/<int:doc_id>/', views.download_report, name='download_report'),

    # API
    path('api/analyse/', views.api_analyse, name='api_analyse'),
]
