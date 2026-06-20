from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from django.utils import timezone
from .models import UserProfile, Document, DocumentVersion, RubricCriterion, PeerEdit, PeerShareRequest, PeerFeedback


class CustomAdminSite(admin.AdminSite):
    site_header = 'StemScribe Admin'
    site_title = 'StemScribe'
    index_title = 'Learning Management Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_dashboard), name='analytics'),
            path('analytics/students/', self.admin_view(self.student_analytics), name='student_analytics'),
            path('analytics/teachers/', self.admin_view(self.teacher_analytics), name='teacher_analytics'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['analytics_link'] = '/admin/analytics/'
        return super().index(request, extra_context=extra_context)

    def analytics_dashboard(self, request):
        """Learning analytics dashboard for admin."""

        # User statistics
        students = User.objects.filter(profile__role='student')
        teachers = User.objects.filter(profile__role='teacher')
        total_students = students.count()
        total_teachers = teachers.count()

        # Document statistics
        total_documents = Document.objects.count()
        students_with_docs = students.filter(documents__isnull=False).distinct().count()
        students_without_docs = total_students - students_with_docs

        # Document upload breakdown
        total_uploads = DocumentVersion.objects.filter(version_type='upload').count()
        avg_docs_per_student = (
            Document.objects.values('owner').distinct().count() / total_students
            if total_students > 0 else 0
        )

        # Engagement metrics
        active_students = students.filter(
            Q(documents__isnull=False) |
            Q(feedbacks_given__isnull=False) |
            Q(edits_given__isnull=False)
        ).distinct().count()

        # Peer review activity
        total_peer_reviews = PeerFeedback.objects.count()
        submitted_reviews = PeerFeedback.objects.filter(is_submitted=True).count()
        total_share_requests = PeerShareRequest.objects.count()

        # Score data
        all_scores = DocumentVersion.objects.filter(version_type='ai_feedback', ai_scores__gt='{}')
        avg_understanding = 0
        avg_analysis = 0
        avg_communication = 0

        if all_scores.exists():
            understanding_scores = []
            analysis_scores = []
            communication_scores = []

            for version in all_scores:
                scores = version.get_scores()
                if 'understanding' in scores and isinstance(scores['understanding'], dict):
                    vals = list(scores['understanding'].values())
                    if vals:
                        understanding_scores.append(sum(vals) / len(vals))
                if 'analysis' in scores and isinstance(scores['analysis'], dict):
                    vals = list(scores['analysis'].values())
                    if vals:
                        analysis_scores.append(sum(vals) / len(vals))
                if 'communication' in scores and isinstance(scores['communication'], dict):
                    vals = list(scores['communication'].values())
                    if vals:
                        communication_scores.append(sum(vals) / len(vals))

            avg_understanding = round(sum(understanding_scores) / len(understanding_scores)) if understanding_scores else 0
            avg_analysis = round(sum(analysis_scores) / len(analysis_scores)) if analysis_scores else 0
            avg_communication = round(sum(communication_scores) / len(communication_scores)) if communication_scores else 0

        # Peer contribution scores
        peer_feedbacks_with_scores = PeerFeedback.objects.filter(scored=True)
        avg_contribution_score = (
            peer_feedbacks_with_scores.aggregate(avg=Avg('ai_contribution_score'))['avg'] or 0
        )
        if avg_contribution_score:
            avg_contribution_score = round(avg_contribution_score)

        # Teacher activity
        teachers_with_rubrics = teachers.filter(rubric_criteria__isnull=False).distinct().count()
        teachers_with_comments = teachers.filter(teacher_comments__isnull=False).distinct().count()

        # Rubric criteria count
        total_rubric_criteria = RubricCriterion.objects.count()

        context = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'students_with_docs': students_with_docs,
            'students_without_docs': students_without_docs,
            'total_documents': total_documents,
            'total_uploads': total_uploads,
            'avg_docs_per_student': round(avg_docs_per_student, 2),
            'active_students': active_students,
            'total_peer_reviews': total_peer_reviews,
            'submitted_reviews': submitted_reviews,
            'total_share_requests': total_share_requests,
            'avg_understanding': avg_understanding,
            'avg_analysis': avg_analysis,
            'avg_communication': avg_communication,
            'avg_contribution_score': avg_contribution_score,
            'teachers_with_rubrics': teachers_with_rubrics,
            'teachers_with_comments': teachers_with_comments,
            'total_rubric_criteria': total_rubric_criteria,
            'peer_feedbacks_with_scores': peer_feedbacks_with_scores.count(),
            'now': timezone.now(),
        }

        return render(request, 'admin/analytics_dashboard.html', context)

    def student_analytics(self, request):
        """Detailed student analytics."""
        students = User.objects.filter(profile__role='student').select_related('profile')

        student_stats = []
        for student in students:
            docs = Document.objects.filter(owner=student)
            doc_count = docs.count()

            versions = DocumentVersion.objects.filter(document__owner=student)
            upload_count = versions.filter(version_type='upload').count()

            feedbacks_given = PeerFeedback.objects.filter(reviewer=student, is_submitted=True).count()
            feedbacks_received = PeerFeedback.objects.filter(share_request__created_by=student).count()
            shares_created = PeerShareRequest.objects.filter(created_by=student).count()

            latest_score = 0
            if versions.exists():
                latest_version = versions.filter(version_type='ai_feedback').order_by('-created_at').first()
                if latest_version:
                    scores = latest_version.get_scores()
                    all_vals = []
                    for pillar in scores.values():
                        if isinstance(pillar, dict):
                            all_vals.extend(pillar.values())
                    latest_score = round(sum(all_vals) / len(all_vals)) if all_vals else 0

            is_active = doc_count > 0 or feedbacks_given > 0 or shares_created > 0

            student_stats.append({
                'student': student,
                'doc_count': doc_count,
                'upload_count': upload_count,
                'feedbacks_given': feedbacks_given,
                'feedbacks_received': feedbacks_received,
                'shares_created': shares_created,
                'latest_score': latest_score,
                'is_active': is_active,
            })

        context = {
            'student_stats': student_stats,
            'total_students': len(student_stats),
            'active_students': sum(1 for s in student_stats if s['is_active']),
            'now': timezone.now(),
        }

        return render(request, 'admin/student_analytics.html', context)

    def teacher_analytics(self, request):
        """Detailed teacher analytics."""
        teachers = User.objects.filter(profile__role='teacher').select_related('profile')

        teacher_stats = []
        for teacher in teachers:
            rubric_criteria = RubricCriterion.objects.filter(teacher=teacher).count()
            comments = TeacherComment.objects.filter(teacher=teacher).count()

            # Get classes taught (from documents of their students if tracked)
            student_users = User.objects.filter(profile__role='student')
            related_docs = Document.objects.filter(owner__in=student_users)

            teacher_stats.append({
                'teacher': teacher,
                'rubric_criteria_count': rubric_criteria,
                'comment_count': comments,
                'is_active': rubric_criteria > 0 or comments > 0,
            })

        context = {
            'teacher_stats': teacher_stats,
            'total_teachers': len(teacher_stats),
            'active_teachers': sum(1 for t in teacher_stats if t['is_active']),
            'now': timezone.now(),
        }

        return render(request, 'admin/teacher_analytics.html', context)


admin_site = CustomAdminSite(name='admin')

# Register models
admin_site.register(UserProfile)
admin_site.register(Document)
admin_site.register(DocumentVersion)
admin_site.register(RubricCriterion)
admin_site.register(PeerEdit)
admin_site.register(PeerShareRequest)
admin_site.register(PeerFeedback)
