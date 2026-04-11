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

    # API
    path('api/analyse/', views.api_analyse, name='api_analyse'),
]
