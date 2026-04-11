import json
import urllib.request
import urllib.error
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserProfile, Document, DocumentVersion, RubricCriterion, PeerEdit

# ──────────────────────────────────────────
# DEMO DATA
# ──────────────────────────────────────────
SAMPLE_REPORT = """Introduction
Amylase is an enzyme that breaks down starch into sugars by providing activation energy to the reaction. As tempsrature increases, enzyme activity increases because particles move faster. This experiment investigates how heat affects enzymes.

Method
We mixed starch solution with amylase and placed this in water baths at 10°C, 30°C, 50°C and 80°C. The time taken for the solution to stop turning blue-black with iodine was recorded. Equal volumes of enzyme solution were used for each test.

Results
As temperature increased, the reaction time decreased from 120s at 10°C to 30s at 50°C, then increased to 60s at 80°C. This shows that enzyme activity mostly increases with temperature.

Discussion
The results indicate that temperature increases enzyme activity by giving energy to the enzyme. Activity peaked at 50°C and decreased at 80°C, possibly due to minor experimental error. Only one trial per temperature was performed, so the results might be flawed. Overall, the experiment clearly shows that increasing temperature always increases amylase activity."""

IMPROVED_REPORT = """Introduction
Amylase is an enzyme that lowers the activation energy required for the breakdown of starch. As temperature increases, enzyme activity generally increases because molecular collisions occur more frequently. This experiment investigates the effect of temperature on amylase activity.

Method
Starch solution was mixed with amylase and placed in water baths at 10°C, 30°C, 50°C and 80°C. The time taken for the solution to stop turning blue-black with iodine was recorded. Equal volumes of enzyme solution were used for each test.

Results
As temperature increased, the reaction time decreased from 120s at 10°C to 30s at 50°C, then increased to 60s at 80°C. This suggests that enzyme activity increases with temperature up to an optimal point.

Discussion
The results indicate that temperature affects enzyme activity by increasing molecular collisions at moderate temperatures. Activity peaked at 50°C and decreased at 80°C, consistent with the expected denaturation of amylase at high temperatures. Only one trial per temperature was performed, which may limit the reliability of the results. Overall, the experiment suggests that amylase activity is influenced by temperature, with an optimal range below 80°C."""

DEMO_ISSUES = [
    {"type": "understanding", "category": "Scientific accuracy",
     "quote": "breaks down starch into sugars by providing activation energy to the reaction",
     "issue": "Incorrect enzyme role",
     "suggestion": "Amylase lowers the activation energy required for starch hydrolysis — it does not provide activation energy."},
    {"type": "understanding", "category": "Conceptual depth",
     "quote": "enzyme activity increases because particles move faster",
     "issue": "Oversimplified mechanism",
     "suggestion": "Increased temperature raises collision frequency and energy of substrate–enzyme encounters, increasing reaction rate up to the optimum."},
    {"type": "understanding", "category": "Use of terminology",
     "quote": "how heat affects enzymes",
     "issue": "Vague terminology",
     "suggestion": "Rephrase as 'the effect of temperature on amylase activity' for scientific precision."},
    {"type": "analysis", "category": "Critical evaluation",
     "quote": "possibly due to minor experimental error",
     "issue": "Overclaiming without mechanism",
     "suggestion": "The decrease at 80°C is consistent with thermal denaturation of the enzyme active site, not experimental error."},
    {"type": "analysis", "category": "Data interpretation",
     "quote": "clearly shows that increasing temperature always increases amylase activity",
     "issue": "Overclaiming — contradicts data",
     "suggestion": "The data suggest an optimal temperature below 80°C; activity decreases beyond this point."},
    {"type": "communication", "category": "Academic tone",
     "quote": "results might be flawed",
     "issue": "Casual phrasing",
     "suggestion": "Replace with 'which may limit the reliability of the results' for appropriate academic register."},
]

DEMO_SCORES = {
    "understanding": {"scientific_accuracy": 45, "conceptual_depth": 38, "terminology": 52},
    "analysis": {"scientific_reasoning": 55, "data_interpretation": 60, "use_of_evidence": 40, "critical_evaluation": 48},
    "communication": {"clarity": 72, "structure": 75, "academic_tone": 65, "grammar": 80}
}

DEFAULT_RUBRIC = [
    ("understanding", "Scientific accuracy", "Are facts correct? Are concepts used properly? Any misconceptions?", 0),
    ("understanding", "Conceptual depth", "Does the report show real understanding or surface-level statements?", 1),
    ("understanding", "Use of terminology", "Are the correct scientific terms used precisely and appropriately?", 2),
    ("analysis", "Scientific reasoning", "Are there logical cause-effect relationships? Are mechanisms explained properly?", 3),
    ("analysis", "Data interpretation", "Do the conclusions match the data? Are trends analysed correctly?", 4),
    ("analysis", "Use of evidence", "Are claims supported by data? Are references included?", 5),
    ("analysis", "Critical evaluation", "Are limitations discussed? Is uncertainty acknowledged? Is there overclaiming?", 6),
    ("communication", "Clarity and precision", "Is there any vague wording? Are statements specific and concise?", 7),
    ("communication", "Structure and organisation", "Does the report have a logical flow? Are sections clear?", 8),
    ("communication", "Academic tone", "Is the language formal and objective? Has casual phrasing been used?", 9),
    ("communication", "Grammar and technical accuracy", "Are there any SPAG errors?", 10),
]

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────
def ensure_profile(user, role='student'):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
    return profile

def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return 'student'

def pillar_avg(scores, pillar):
    if pillar not in scores:
        return 0
    vals = list(scores[pillar].values())
    return round(sum(vals) / len(vals)) if vals else 0

def overall_avg(scores):
    all_vals = []
    for pillar in scores.values():
        if isinstance(pillar, dict):
            all_vals.extend(pillar.values())
    return round(sum(all_vals) / len(all_vals)) if all_vals else 0

def call_claude(prompt):
    """Call OpenAI ChatGPT API directly via urllib (no external deps)."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None

    payload = json.dumps({
        "model": "gpt-4o",
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            text = data['choices'][0]['message']['content']
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
    except Exception:
        return None

def ensure_demo_doc(user):
    """Create demo document for student if none exist."""
    if not Document.objects.filter(owner=user).exists():
        doc = Document.objects.create(owner=user, title='Enzyme Activity Lab', class_name='BIOL 201')
        # Version 1 - original upload
        v1 = DocumentVersion.objects.create(
            document=doc, content=SAMPLE_REPORT,
            version_type='upload', ai_scores='{}', ai_issues='[]'
        )
        # Version 2 - AI feedback
        DocumentVersion.objects.create(
            document=doc, content=SAMPLE_REPORT,
            version_type='ai_feedback',
            ai_scores=json.dumps(DEMO_SCORES),
            ai_issues=json.dumps(DEMO_ISSUES)
        )
        # Version 3 - improved
        DocumentVersion.objects.create(
            document=doc, content=IMPROVED_REPORT,
            version_type='self_edit',
            ai_scores=json.dumps({
                "understanding": {"scientific_accuracy": 76, "conceptual_depth": 65, "terminology": 78},
                "analysis": {"scientific_reasoning": 72, "data_interpretation": 78, "use_of_evidence": 71, "critical_evaluation": 79},
                "communication": {"clarity": 85, "structure": 90, "academic_tone": 88, "grammar": 92}
            }),
            ai_issues='[]'
        )
        return doc
    return Document.objects.filter(owner=user).first()

def ensure_demo_rubric(teacher):
    if not RubricCriterion.objects.filter(teacher=teacher).exists():
        for pillar, name, desc, order in DEFAULT_RUBRIC:
            RubricCriterion.objects.create(
                teacher=teacher, pillar=pillar, name=name, description=desc, order=order
            )

# ──────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────
def landing(request):
    if request.user.is_authenticated:
        role = get_role(request.user)
        return redirect('student_submit' if role == 'student' else 'teacher_dashboard')
    return render(request, 'core/landing.html')

def login_view(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'student')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'core/landing.html', {'error': 'Invalid email or password.', 'login_role': role})

        ensure_profile(user, role)
        login(request, user)

        if role == 'student':
            ensure_demo_doc(user)
            return redirect('student_submit')
        else:
            ensure_demo_rubric(user)
            return redirect('teacher_dashboard')

    return redirect('landing')

def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'student')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()

        ctx = {'register_role': role, 'reg_username': username, 'reg_full_name': full_name}

        if not username or not password:
            ctx['reg_error'] = 'Email and password are required.'
            return render(request, 'core/landing.html', ctx)

        if password != confirm:
            ctx['reg_error'] = 'Passwords do not match.'
            return render(request, 'core/landing.html', ctx)

        if len(password) < 6:
            ctx['reg_error'] = 'Password must be at least 6 characters.'
            return render(request, 'core/landing.html', ctx)

        if User.objects.filter(username=username).exists():
            ctx['reg_error'] = 'An account with that email already exists.'
            return render(request, 'core/landing.html', ctx)

        user = User.objects.create_user(username=username, password=password)
        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save()

        ensure_profile(user, role)
        login(request, user)

        if role == 'student':
            return redirect('student_submit')
        else:
            ensure_demo_rubric(user)
            return redirect('teacher_dashboard')

    return redirect('landing')

def logout_view(request):
    logout(request)
    return redirect('landing')

# ──────────────────────────────────────────
# STUDENT VIEWS
# ──────────────────────────────────────────
def _student_context(request):
    docs = Document.objects.filter(owner=request.user).order_by('-updated_at')
    peer_edits = PeerEdit.objects.filter(editor=request.user).count()
    return {'documents': docs, 'peer_edit_count': peer_edits, 'user': request.user}

@login_required
def student_submit(request):
    ctx = _student_context(request)
    ctx['page'] = 'submit'
    return render(request, 'core/student_submit.html', ctx)

@login_required
def student_docs(request):
    ctx = _student_context(request)
    ctx['page'] = 'docs'
    return render(request, 'core/student_submit.html', ctx)

@login_required
def howto(request):
    ctx = _student_context(request)
    ctx['page'] = 'howto'
    rubric = RubricCriterion.objects.none()
    # Use any teacher's rubric if available, else default
    ctx['rubric_understanding'] = [
        {'name': 'Scientific accuracy', 'desc': 'Are facts correct? Are concepts used properly? Any misconceptions?'},
        {'name': 'Conceptual depth', 'desc': 'Does the report show real understanding or surface-level statements?'},
        {'name': 'Use of terminology', 'desc': 'Are the correct scientific terms used precisely and appropriately?'},
    ]
    ctx['rubric_analysis'] = [
        {'name': 'Scientific reasoning', 'desc': 'Are there logical cause-effect relationships? Are mechanisms explained properly?'},
        {'name': 'Data interpretation', 'desc': 'Do the conclusions match the data? Are trends analysed correctly?'},
        {'name': 'Use of evidence', 'desc': 'Are claims supported by data? Are references included?'},
        {'name': 'Critical evaluation', 'desc': 'Are limitations discussed? Is uncertainty acknowledged? Is there overclaiming?'},
    ]
    ctx['rubric_communication'] = [
        {'name': 'Clarity and precision', 'desc': 'Is there any vague wording? Are statements specific and concise?'},
        {'name': 'Structure and organisation', 'desc': 'Does the report have a logical flow? Are sections clear?'},
        {'name': 'Academic tone', 'desc': 'Is the language formal and objective? Has casual phrasing been used?'},
        {'name': 'Grammar and technical accuracy', 'desc': 'Are there any SPAG errors?'},
    ]
    return render(request, 'core/student_howto.html', ctx)

@login_required
def student_analyse(request):
    """Handle report submission and trigger AI analysis."""
    if request.method != 'POST':
        return redirect('student_submit')

    content = request.POST.get('report_text', '').strip()
    title = request.POST.get('title', 'Untitled Report').strip() or 'Untitled Report'

    if not content:
        uploaded = request.FILES.get('report_file')
        if uploaded:
            content = uploaded.read().decode('utf-8', errors='ignore')

    if not content:
        return redirect('student_submit')

    # Create or get document
    doc_id = request.POST.get('doc_id')
    if doc_id:
        doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    else:
        doc = Document.objects.create(owner=request.user, title=title, class_name='BIOL 201')

    # Create upload version
    version = DocumentVersion.objects.create(
        document=doc, content=content, version_type='upload'
    )

    # Store pending version in session for async-like flow
    request.session['pending_version_id'] = version.pk
    request.session['pending_doc_id'] = doc.pk
    return redirect('api_analyse')

@login_required
def api_analyse(request):
    """Run AI analysis and redirect to results."""
    version_id = request.session.get('pending_version_id')
    doc_id = request.session.get('pending_doc_id')

    if not version_id:
        return redirect('student_submit')

    version = get_object_or_404(DocumentVersion, pk=version_id)
    doc = version.document

    prompt = f"""You are an AI tutor evaluating a STEM lab report. Analyse this report and return ONLY a JSON object (no markdown, no preamble) with this exact structure:
{{
  "scores": {{
    "understanding": {{"scientific_accuracy": 0-100, "conceptual_depth": 0-100, "terminology": 0-100}},
    "analysis": {{"scientific_reasoning": 0-100, "data_interpretation": 0-100, "use_of_evidence": 0-100, "critical_evaluation": 0-100}},
    "communication": {{"clarity": 0-100, "structure": 0-100, "academic_tone": 0-100, "grammar": 0-100}}
  }},
  "issues": [
    {{
      "type": "understanding|analysis|communication",
      "category": "Scientific accuracy|Conceptual depth|Use of terminology|Scientific reasoning|Data interpretation|Use of evidence|Critical evaluation|Clarity and precision|Structure and organisation|Academic tone|Grammar and technical accuracy",
      "quote": "exact problematic phrase from the report (max 20 words)",
      "issue": "Brief issue label",
      "suggestion": "Improved version (max 35 words)"
    }}
  ]
}}
Provide 4-6 issues. Be specific. Quote EXACT phrases verbatim from the report.

REPORT:
{version.content}"""

    result = call_claude(prompt)

    if result and 'scores' in result and 'issues' in result:
        scores = result['scores']
        issues = result['issues']
    else:
        scores = DEMO_SCORES
        issues = DEMO_ISSUES

    # Save AI feedback version
    ai_version = DocumentVersion.objects.create(
        document=doc,
        content=version.content,
        version_type='ai_feedback',
        ai_scores=json.dumps(scores),
        ai_issues=json.dumps(issues)
    )

    doc.save()  # update updated_at
    request.session.pop('pending_version_id', None)
    request.session.pop('pending_doc_id', None)
    request.session['active_version_id'] = ai_version.pk

    return redirect('student_analysis', doc_id=doc.pk)

@login_required
def student_analysis(request, doc_id):
    role = get_role(request.user)
    if role == 'teacher':
        doc = get_object_or_404(Document, pk=doc_id)
    else:
        doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    version_id = request.session.get('active_version_id')
    if version_id:
        try:
            version = DocumentVersion.objects.get(pk=version_id, document=doc)
        except DocumentVersion.DoesNotExist:
            version = doc.versions.order_by('-created_at').first()
    else:
        version = doc.versions.filter(version_type='ai_feedback').order_by('-created_at').first()
        if not version:
            version = doc.versions.order_by('-created_at').first()

    scores = version.get_scores() if version else {}
    issues = version.get_issues() if version else []

    approved_indices = request.session.get(f'approved_{version.pk}', []) if version else []

    ctx = _student_context(request)
    ctx.update({
        'page': 'analysis',
        'doc': doc,
        'version': version,
        'scores': scores,
        'issues': issues,
        'issues_json': json.dumps(issues),
        'approved_indices': approved_indices,
        'u_score': pillar_avg(scores, 'understanding'),
        'a_score': pillar_avg(scores, 'analysis'),
        'c_score': pillar_avg(scores, 'communication'),
        'overall': overall_avg(scores),
    })
    return render(request, 'core/student_analysis.html', ctx)

@login_required
@require_POST
def approve_edit(request):
    data = json.loads(request.body)
    version_id = data.get('version_id')
    issue_index = data.get('issue_index')
    action = data.get('action', 'approve')

    version = get_object_or_404(DocumentVersion, pk=version_id)
    doc = version.document
    if doc.owner != request.user and get_role(request.user) != 'teacher':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    key = f'approved_{version_id}'
    approved = request.session.get(key, [])

    if action == 'approve' and issue_index not in approved:
        approved.append(issue_index)
        issues = version.get_issues()
        if 0 <= issue_index < len(issues):
            issue = issues[issue_index]
            # Create self-edit version with the change applied
            new_content = version.content.replace(issue['quote'], issue['suggestion'], 1)
            DocumentVersion.objects.create(
                document=doc,
                content=new_content,
                version_type='self_edit',
                ai_scores=version.ai_scores,
                ai_issues=version.ai_issues
            )
            doc.save()

    request.session[key] = approved
    return JsonResponse({'ok': True, 'approved': approved})

@login_required
def student_version_history(request, doc_id):
    if get_role(request.user) == 'teacher':
        doc = get_object_or_404(Document, pk=doc_id)
    else:
        doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    versions = doc.versions.order_by('-created_at')
    selected_id = request.GET.get('v')
    selected = None
    if selected_id:
        try:
            selected = versions.get(pk=selected_id)
        except DocumentVersion.DoesNotExist:
            pass
    if not selected:
        selected = versions.first()

    ctx = _student_context(request)
    scores = selected.get_scores() if selected else {}
    ctx.update({
        'page': 'version',
        'doc': doc,
        'versions': versions,
        'selected': selected,
        'scores': scores,
        'u_score': pillar_avg(scores, 'understanding'),
        'a_score': pillar_avg(scores, 'analysis'),
        'c_score': pillar_avg(scores, 'communication'),
        'overall': overall_avg(scores),
        'sub_scores': {
            'understanding': [
                ('Scientific accuracy', scores.get('understanding', {}).get('scientific_accuracy', '—')),
                ('Conceptual depth', scores.get('understanding', {}).get('conceptual_depth', '—')),
                ('Terminology', scores.get('understanding', {}).get('terminology', '—')),
            ],
            'analysis': [
                ('Scientific reasoning', scores.get('analysis', {}).get('scientific_reasoning', '—')),
                ('Data interpretation', scores.get('analysis', {}).get('data_interpretation', '—')),
                ('Use of evidence', scores.get('analysis', {}).get('use_of_evidence', '—')),
                ('Critical evaluation', scores.get('analysis', {}).get('critical_evaluation', '—')),
            ],
            'communication': [
                ('Clarity', scores.get('communication', {}).get('clarity', '—')),
                ('Structure', scores.get('communication', {}).get('structure', '—')),
                ('Academic tone', scores.get('communication', {}).get('academic_tone', '—')),
                ('Grammar', scores.get('communication', {}).get('grammar', '—')),
            ],
        }
    })
    return render(request, 'core/student_version.html', ctx)

@login_required
def student_dashboard(request, doc_id):
    if get_role(request.user) == 'teacher':
        doc = get_object_or_404(Document, pk=doc_id)
    else:
        doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    versions = list(doc.versions.order_by('created_at'))
    first = versions[0] if versions else None
    latest = versions[-1] if versions else None

    first_scores = first.get_scores() if first else {}
    latest_scores = latest.get_scores() if latest else {}

    peer_edits_given = PeerEdit.objects.filter(editor=request.user)
    total_impact = sum(p.total_impact for p in peer_edits_given)

    ctx = _student_context(request)
    ctx.update({
        'page': 'dashboard',
        'doc': doc,
        'versions': versions,
        'first_overall': overall_avg(first_scores),
        'latest_overall': overall_avg(latest_scores),
        'improvement': overall_avg(latest_scores) - overall_avg(first_scores),
        'u_improvement': pillar_avg(latest_scores, 'understanding') - pillar_avg(first_scores, 'understanding'),
        'a_improvement': pillar_avg(latest_scores, 'analysis') - pillar_avg(first_scores, 'analysis'),
        'c_improvement': pillar_avg(latest_scores, 'communication') - pillar_avg(first_scores, 'communication'),
        'peer_edits_given': peer_edits_given,
        'total_impact': total_impact,
        'version_scores': [(v, overall_avg(v.get_scores())) for v in versions],
        'expertise_pct': min(100, 20 + total_impact),
    })
    return render(request, 'core/student_dashboard.html', ctx)

# ──────────────────────────────────────────
# TEACHER VIEWS
# ──────────────────────────────────────────
def _teacher_context(request):
    students = User.objects.filter(profile__role='student').exclude(pk=request.user.pk)
    criteria = RubricCriterion.objects.filter(teacher=request.user)
    return {'students': students, 'rubric': criteria, 'user': request.user}

@login_required
def teacher_dashboard(request):
    ctx = _teacher_context(request)
    students = ctx['students']

    # Compute class averages
    all_scores = {'understanding': [], 'analysis': [], 'communication': []}
    for s in students:
        latest_docs = Document.objects.filter(owner=s)
        for doc in latest_docs:
            v = doc.versions.order_by('-created_at').first()
            if v and v.get_scores():
                sc = v.get_scores()
                for pillar in all_scores:
                    avg = pillar_avg(sc, pillar)
                    if avg:
                        all_scores[pillar].append(avg)

    def safe_avg(lst):
        return round(sum(lst) / len(lst)) if lst else 0

    ctx.update({
        'page': 'dashboard',
        'class_name': 'BIOL 201',
        'student_count': students.count(),
        'u_avg': safe_avg(all_scores['understanding']),
        'a_avg': safe_avg(all_scores['analysis']),
        'c_avg': safe_avg(all_scores['communication']),
        'overall_avg': safe_avg(all_scores['understanding'] + all_scores['analysis'] + all_scores['communication']),
    })
    return render(request, 'core/teacher_dashboard.html', ctx)

@login_required
def teacher_stats(request):
    ctx = _teacher_context(request)
    students = ctx['students']
    student_data = []
    for s in students:
        docs = Document.objects.filter(owner=s)
        latest_v = None
        for doc in docs:
            v = doc.versions.order_by('-created_at').first()
            if v and v.get_scores():
                latest_v = v
                break
        scores = latest_v.get_scores() if latest_v else {}
        impact = sum(PeerEdit.objects.filter(editor=s).values_list('score_impact_understanding', flat=True)) + \
                 sum(PeerEdit.objects.filter(editor=s).values_list('score_impact_analysis', flat=True)) + \
                 sum(PeerEdit.objects.filter(editor=s).values_list('score_impact_communication', flat=True))
        student_data.append({
            'user': s,
            'doc_count': docs.count(),
            'u_score': pillar_avg(scores, 'understanding'),
            'a_score': pillar_avg(scores, 'analysis'),
            'c_score': pillar_avg(scores, 'communication'),
            'overall': overall_avg(scores),
            'impact': impact,
        })

    ctx.update({'page': 'stats', 'student_data': student_data})
    return render(request, 'core/teacher_stats.html', ctx)

@login_required
def teacher_student(request, student_id):
    student = get_object_or_404(User, pk=student_id)
    docs = Document.objects.filter(owner=student).order_by('-updated_at')
    peer_edits = PeerEdit.objects.filter(editor=student)
    latest_version = None
    scores = {}
    for doc in docs:
        v = doc.versions.order_by('-created_at').first()
        if v:
            latest_version = v
            scores = v.get_scores()
            break

    ctx = _teacher_context(request)
    ctx.update({
        'page': 'student',
        'student': student,
        'docs': docs,
        'peer_edits': peer_edits,
        'u_score': pillar_avg(scores, 'understanding'),
        'a_score': pillar_avg(scores, 'analysis'),
        'c_score': pillar_avg(scores, 'communication'),
        'overall': overall_avg(scores),
    })
    return render(request, 'core/teacher_student.html', ctx)

@login_required
def teacher_rubric(request):
    ensure_demo_rubric(request.user)
    ctx = _teacher_context(request)
    ctx['page'] = 'rubric'
    ctx['understanding'] = RubricCriterion.objects.filter(teacher=request.user, pillar='understanding')
    ctx['analysis'] = RubricCriterion.objects.filter(teacher=request.user, pillar='analysis')
    ctx['communication'] = RubricCriterion.objects.filter(teacher=request.user, pillar='communication')
    return render(request, 'core/teacher_rubric.html', ctx)

@login_required
@require_POST
def teacher_rubric_save(request):
    pillar = request.POST.get('pillar')
    name = request.POST.get('name', '').strip()
    desc = request.POST.get('description', '').strip()
    pk = request.POST.get('pk')
    if pk:
        c = get_object_or_404(RubricCriterion, pk=pk, teacher=request.user)
        c.name = name
        c.description = desc
        c.save()
    else:
        RubricCriterion.objects.create(teacher=request.user, pillar=pillar, name=name, description=desc)
    return redirect('teacher_rubric')

@login_required
def teacher_rubric_delete(request, pk):
    c = get_object_or_404(RubricCriterion, pk=pk, teacher=request.user)
    c.delete()
    return redirect('teacher_rubric')

@login_required
def teacher_upload(request):
    ctx = _teacher_context(request)
    ctx['page'] = 'upload'
    return render(request, 'core/teacher_upload.html', ctx)

@login_required
def teacher_class_feedback(request):
    ctx = _teacher_context(request)
    ctx['page'] = 'feedback'
    return render(request, 'core/teacher_feedback.html', ctx)
