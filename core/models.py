from django.db import models
from django.contrib.auth.models import User
import json


class UserProfile(models.Model):
    ROLE_CHOICES = [('student', 'Student'), ('teacher', 'Teacher')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    class_name = models.CharField(max_length=100, blank=True, default='BIOL 201')

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200, default='Untitled Report')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class_name = models.CharField(max_length=100, blank=True, default='BIOL 201')

    def __str__(self):
        return self.title

    def latest_version(self):
        return self.versions.order_by('-created_at').first()

    def version_count(self):
        return self.versions.count()


class DocumentVersion(models.Model):
    VERSION_TYPE_CHOICES = [
        ('upload', 'Uploaded document'),
        ('ai_feedback', 'AI feedback'),
        ('self_edit', 'Self edit'),
        ('peer_edit', 'Peer edit'),
    ]
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    version_type = models.CharField(max_length=20, choices=VERSION_TYPE_CHOICES, default='upload')
    created_at = models.DateTimeField(auto_now_add=True)
    ai_scores = models.TextField(blank=True, default='{}')   # JSON
    ai_issues = models.TextField(blank=True, default='[]')   # JSON

    def get_scores(self):
        try:
            return json.loads(self.ai_scores)
        except Exception:
            return {}

    def get_issues(self):
        try:
            return json.loads(self.ai_issues)
        except Exception:
            return []

    def overall_score(self):
        scores = self.get_scores()
        if not scores:
            return None
        all_vals = []
        for pillar in scores.values():
            if isinstance(pillar, dict):
                all_vals.extend(pillar.values())
        return round(sum(all_vals) / len(all_vals)) if all_vals else None

    def pillar_score(self, pillar):
        scores = self.get_scores()
        if pillar not in scores:
            return None
        vals = list(scores[pillar].values())
        return round(sum(vals) / len(vals)) if vals else None

    class Meta:
        ordering = ['created_at']


class RubricCriterion(models.Model):
    PILLAR_CHOICES = [
        ('understanding', 'Understanding'),
        ('analysis', 'Analysis'),
        ('communication', 'Communication'),
    ]
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rubric_criteria')
    pillar = models.CharField(max_length=20, choices=PILLAR_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['pillar', 'order']

    def __str__(self):
        return f"{self.pillar} — {self.name}"


class PeerEdit(models.Model):
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edits_given')
    target_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name='peer_edits')
    created_at = models.DateTimeField(auto_now_add=True)
    score_impact_understanding = models.IntegerField(default=0)
    score_impact_analysis = models.IntegerField(default=0)
    score_impact_communication = models.IntegerField(default=0)

    @property
    def total_impact(self):
        return self.score_impact_understanding + self.score_impact_analysis + self.score_impact_communication


class PeerShareRequest(models.Model):
    SECTION_CHOICES = [
        ('introduction', 'Introduction'),
        ('method', 'Method'),
        ('results', 'Results'),
        ('discussion', 'Discussion'),
        ('conclusion', 'Conclusion'),
        ('custom', 'Custom section'),
    ]
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='share_requests')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_created')
    section_label = models.CharField(max_length=50, choices=SECTION_CHOICES, default='custom')
    section_text = models.TextField()
    question = models.TextField(blank=True)
    shared_with = models.ManyToManyField(User, blank=True, related_name='received_shares')  # empty = all students
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_by.username} — {self.get_section_label_display()}"

    def feedback_count(self):
        return self.feedbacks.count()


class PeerFeedback(models.Model):
    share_request = models.ForeignKey(PeerShareRequest, on_delete=models.CASCADE, related_name='feedbacks')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_given')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ai_contribution_score = models.IntegerField(default=0)  # 0–100 overall
    ai_score_detail = models.TextField(blank=True, default='{}')  # JSON
    scored = models.BooleanField(default=False)

    def get_score_detail(self):
        try:
            return json.loads(self.ai_score_detail)
        except Exception:
            return {}
