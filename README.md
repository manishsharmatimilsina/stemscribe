# StemScribe — AI-Guided STEM Writing Platform

An intelligent Django-based collaborative learning platform for STEM education. Students submit lab reports, receive AI-powered feedback, participate in structured peer review, and collaborate with classmates through a quality-assured feedback system. Teachers monitor class progress, provide oversight on peer contributions, and guide skill development through custom rubrics.

**Key Differentiator:** The peer review system uses AI quality assurance—peers submit feedback drafts, AI scores them on Specificity/Constructiveness/Scientific Accuracy, and peers can revise their feedback based on AI suggestions before it reaches the student.

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Quick Start](#quick-start)
4. [Features & Workflows](#features--workflows)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Deployment](#deployment)
8. [Development](#development)
9. [Troubleshooting](#troubleshooting)

---

## Installation

### System Requirements

- **Python:** 3.8+
- **Database:** SQLite (included) or PostgreSQL for production
- **OS:** macOS, Linux, Windows (with WSL recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/manishsharmatimilsina/stemscribe.git
cd stemscribe/stemscribe
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Then access admin panel at `http://localhost:8000/admin`

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: OpenAI API key for AI feedback generation
OPENAI_API_KEY=sk-your-key-here

# Optional: Django secret key (auto-generated if not set)
SECRET_KEY=your-secret-key-here

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Optional: Debug mode (set to False in production)
DEBUG=True

# Optional: Allowed hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1,159.65.240.114

# Optional: CORS settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://159.65.240.114
```

### Django Settings

Key configuration in `stemscribe/settings.py`:

```python
# Enable/disable AI features
USE_OPENAI_API = True  # Set to False for demo mode

# Document upload settings
MAX_UPLOAD_SIZE = 5_000_000  # 5MB

# Supported file formats
SUPPORTED_FORMATS = ['txt', 'pdf', 'docx']

# Peer review section types
SECTION_CHOICES = [
    'introduction', 'method', 'results', 'discussion', 'conclusion', 'custom'
]

# AI scoring dimensions for peer feedback
FEEDBACK_SCORING_DIMENSIONS = {
    'specificity': 'Is the feedback detailed and specific?',
    'constructiveness': 'Is it balanced and actionable?',
    'scientific_accuracy': 'Is it technically correct?'
}
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# 4. Start the development server
python manage.py runserver

# 5. Open in browser
# http://127.0.0.1:8000
```

### Demo Accounts

Register with any email/password combination, or use these examples:

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Student | student@imperial.ac.uk | demo1234 | Can submit reports, give peer feedback |
| Teacher | teacher@imperial.ac.uk | demo1234 | Dashboard, rubric, peer oversight |

**Important:** Registration creates new accounts automatically. Both students and teachers register and select their role during signup.

---

## Features & Workflows

### 1. Student Report Submission & Analysis

**Entry Point:** `/student/submit/`

#### Submission Methods

- **Paste:** Copy-paste text directly into textarea
- **Upload:** .txt, .pdf, .docx files (max 5MB)
- **URL:** Link to external document (future feature)

#### Document Processing

1. Student submits report
2. Django extracts text (handles PDF/DOCX conversion)
3. OpenAI Claude API analyzes report against three dimensions:
   - **Understanding:** Comprehension of concepts, proper definitions, theoretical grounding
   - **Analysis:** Critical thinking, data interpretation, methodology soundness
   - **Communication:** Clarity, organization, grammar, scientific writing conventions
4. AI returns:
   - Overall score (0–100) for each dimension
   - Detailed issues with exact line numbers and suggestions
   - Color-coded highlights (red = critical, yellow = minor, green = suggestions)

#### Feedback Review

Student views the highlighted report with inline issue marks. For each issue:
- Click to expand detail and suggestion
- Approve: Applies suggested change, creates new DocumentVersion (version_type='ai_feedback')
- Reject: Dismisses issue without action
- Edit: Manually modify the suggestion before approving

#### Version Tracking

Every approval action creates a new `DocumentVersion` with:
- Full document content post-edits
- AI scores from that analysis session
- Metadata: timestamp, version type, editor

Students can browse version history and compare scores across submissions.

---

### 2. Peer Review System

**Core Concept:** Quality-assured peer feedback through AI review before submission.

#### Peer Contribution Workflow

**Step 1: Student Shares a Section**
- Entry Point: `/student/analysis/<doc_id>/share-section/`
- Student selects section type (Introduction, Method, Results, Discussion, Conclusion, or Custom)
- Optional: Include a guiding question for reviewers (e.g., "Does my methodology clearly justify my approach?")
- Click "Share for peer review"
- Creates `PeerShareRequest` record with `is_open=True`

**Step 2: Peers Discover Requests**
- Entry Point: `/peer/feed/`
- Students browse all open peer requests from classmates
- Filter by section type or class
- Click to review a specific request

**Step 3: Peer Submits Draft Feedback**
- Entry Point: `/peer/review/<share_id>/`
- Peer reads the shared section + optional author question
- Types feedback in textarea (encouraged to be specific, constructive, actionable)
- Clicks "Save & review with AI"
- Creates `PeerFeedback` record with `is_submitted=False` (draft state)

**Step 4: AI Review & Scoring**
- Backend calls `_score_peer_feedback()` function
- OpenAI Claude analyzes the peer's feedback on:
  - **Specificity** (0–100): Is it detailed? Does it point to specific phrases/issues?
  - **Constructiveness** (0–100): Is it balanced? Does it offer improvement suggestions?
  - **Scientific Accuracy** (0–100): Is the feedback technically correct?
- Calculates overall `ai_contribution_score` as average of three dimensions
- Generates `ai_feedback_text` with specific suggestions to improve the peer's feedback
- Sets `ai_feedback_generated=True`, `scored=True`

**Step 5: Peer Reviews AI Suggestions & Edits**
- Peer returns to same page and sees:
  - Their draft feedback in a box
  - AI scores with dimension breakdown
  - AI suggestions (e.g., "You could be more specific about which methods need justification")
- Peer can:
  - Click "Edit feedback" → `/peer/edit/<feedback_id>/`
  - Revise based on AI suggestions
  - Click "Save & re-score ✨" to get new AI scoring

**Step 6: Peer Submits Final Feedback**
- Once satisfied, peer clicks "Send to student →"
- Sets `is_submitted=True`
- Feedback now appears in student's document view (read-only from peer perspective)
- Peer can no longer edit once submitted

#### Peer Activity Dashboard
- Entry Point: `/peer/activity/`
- Shows:
  - **Feedback Given:** All submitted feedback with AI scores and edit links for drafts
  - **Feedback Received:** All feedback from peers on student's shared sections
  - **Average Score:** Overall peer contribution score (average of all submitted feedback scores)
- Incentivizes quality contributions through visible scoring

---

### 3. Student Document View & Collaboration

**Entry Point:** `/student/analysis/<doc_id>/`

#### Document Display

- Full report text with proper formatting (paragraphs, line breaks preserved)
- Section headers auto-detected and formatted
- In-context feedback panels:
  - AI feedback with issue details and suggestions
  - Peer feedback (submitted) with contributor scores and "View thread" link
  - Teacher comments with edit/delete options (teachers only)

#### Actions Available

- **Edit inline:** Click "Edit & revise" to modify report sections
- **Download:** Export formatted report to PDF/DOCX
- **View versions:** Sidebar shows version history with score progression
- **Peer thread:** Click feedback to view full peer review thread with all responses

#### Version History

Sidebar shows:
- Version count and creation date
- Overall score trend (visualization)
- Clickable versions to compare scores side-by-side

---

### 4. Teacher Dashboard & Oversight

#### Dashboard Overview
- Entry Point: `/teacher/dashboard/`
- Statistics tab: Class-wide metrics (average scores, engagement stats)
- Student list with flags:
  - Red: Low participation or struggling students
  - Green: Top collaborators and high performers

#### Per-Student View
- Entry Point: `/teacher/student/<student_id>/`
- All documents and versions for a specific student
- All peer feedback they've received (with contributor info)
- Teacher comments (add, edit, delete)
- Score breakdown by Understanding/Analysis/Communication

#### Peer Feedback Oversight
- Entry Point: `/teacher/peer-overview/`
- Leaderboard: Class rankings by peer contribution score
- Activity log: Timestamp, reviewer, reviewee, section, feedback quality score
- Identify: Top peer reviewers, at-risk students (low feedback quality), disengaged students

#### Rubric Management
- Entry Point: `/teacher/rubric/`
- Add/edit/delete custom criteria under each pillar:
  - Understanding (conceptual, definitions, theory)
  - Analysis (critical thinking, data interpretation)
  - Communication (clarity, organization, grammar)
- Criteria feed AI prompts for analysis (customizable per class)

#### Class Upload
- Entry Point: `/teacher/upload/`
- Bulk upload student documents (CSV of emails + document files)
- Useful for batch loading lab reports at semester start

---

## Database Schema

### Core Models

#### UserProfile
```python
class UserProfile(models.Model):
    user: OneToOneField(User)
    role: CharField(choices=['student', 'teacher'])
    class_name: CharField(default='BIOL 201')
```
Links Django User to application role and class assignment.

#### Document
```python
class Document(models.Model):
    owner: ForeignKey(User)  # Student who submitted
    title: CharField(default='Untitled Report')
    class_name: CharField(default='BIOL 201')
    created_at: DateTimeField(auto_now_add=True)
    updated_at: DateTimeField(auto_now=True)
```
Container for all versions of a student's report.

#### DocumentVersion
```python
class DocumentVersion(models.Model):
    document: ForeignKey(Document)
    content: TextField()  # Full report text
    version_type: CharField(choices=[
        'upload',        # Original submission
        'ai_feedback',   # Student approved AI suggestions
        'self_edit',     # Manual student edits
        'peer_edit'      # Incorporating peer feedback
    ])
    ai_scores: TextField()    # JSON: {Understanding, Analysis, Communication}
    ai_issues: TextField()    # JSON: [{line, type, suggestion}]
    created_at: DateTimeField(auto_now_add=True)
```
Immutable historical record of each document state.

#### PeerShareRequest
```python
class PeerShareRequest(models.Model):
    document: ForeignKey(Document)
    created_by: ForeignKey(User)  # Student sharing section
    section_label: CharField(choices=[
        'introduction', 'method', 'results', 'discussion', 'conclusion', 'custom'
    ])
    section_text: TextField()  # The actual section content
    question: TextField(blank=True)  # Optional author's question
    shared_with: ManyToManyField(User, blank=True)  # Empty = all students can review
    is_open: BooleanField(default=True)  # Closed when author no longer wants feedback
    created_at: DateTimeField(auto_now_add=True)
```
Request for peer feedback on a specific document section.

#### PeerFeedback
```python
class PeerFeedback(models.Model):
    share_request: ForeignKey(PeerShareRequest)
    reviewer: ForeignKey(User)  # Student giving feedback
    feedback_text: TextField()
    is_submitted: BooleanField(default=False)  # False = draft, True = sent to author
    created_at: DateTimeField(auto_now_add=True)
    updated_at: DateTimeField(auto_now=True)
    
    # AI Scoring (populated after initial draft submission)
    ai_contribution_score: IntegerField(default=0)  # 0–100 overall
    ai_score_detail: TextField()  # JSON: {specificity, constructiveness, scientific_accuracy, summary}
    scored: BooleanField(default=False)
    ai_feedback_text: TextField(blank=True)  # AI suggestions to improve this feedback
    ai_feedback_generated: BooleanField(default=False)
```
Feedback from one peer to another, with AI quality assurance workflow.

#### TeacherComment
```python
class TeacherComment(models.Model):
    teacher: ForeignKey(User)
    document: ForeignKey(Document)
    text: TextField()
    created_at: DateTimeField(auto_now_add=True)
```
Teacher annotations on student documents.

#### RubricCriterion
```python
class RubricCriterion(models.Model):
    teacher: ForeignKey(User)
    pillar: CharField(choices=['understanding', 'analysis', 'communication'])
    name: CharField()  # E.g., "Clear methodology description"
    description: TextField()  # Full grading rubric text
    order: IntegerField(default=0)
```
Custom grading criteria defined by teacher.

---

## API Endpoints

All endpoints require login. Django sessions handle authentication.

### Student Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/student/dashboard/` | Personal stats and quick links |
| GET/POST | `/student/submit/` | Upload/paste new report |
| GET | `/student/analysis/<doc_id>/` | View report with feedback |
| POST | `/student/analysis/<doc_id>/save-revision/` | Save inline edits |
| POST | `/student/analysis/<doc_id>/download/` | Export report as file |
| GET/POST | `/student/analysis/<doc_id>/share-section/` | Share section for peer review |
| GET/POST | `/student/version/<doc_id>/` | View/compare versions |
| GET | `/student/howto/` | Platform guide |

### Peer Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/peer/feed/` | Browse open peer requests |
| GET/POST | `/peer/review/<share_id>/` | View request and submit/edit feedback |
| POST | `/peer/review/<share_id>/` (action=submit) | Submit drafted feedback to student |
| GET/POST | `/peer/edit/<feedback_id>/` | Edit drafted feedback based on AI suggestions |
| POST | `/peer/close/<share_id>/` | Author closes peer request |
| GET | `/peer/activity/` | View contribution stats and history |

### Teacher Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/teacher/dashboard/` | Class statistics and student flags |
| GET | `/teacher/student/<student_id>/` | Per-student view and comments |
| GET | `/teacher/peer-overview/` | Peer feedback leaderboard and activity |
| GET/POST | `/teacher/rubric/` | Define custom grading criteria |
| GET/POST | `/teacher/upload/` | Bulk upload student documents |

### Authentication Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Landing page (before login) |
| GET/POST | `/register/` | New account creation |
| GET | `/login/` | Login form |
| POST | `/logout/` | Logout (redirects to landing) |
| GET | `/admin/` | Django admin (superuser only) |

---

## AI Scoring Details

### Report Analysis Prompt

When a student submits a report, the system calls OpenAI with:

```
Analyze this STEM lab report on three dimensions:

1. Understanding (0–100): 
   - Does the student grasp key concepts?
   - Are definitions correct and properly cited?
   - Is theory grounded in course material?

2. Analysis (0–100):
   - Is reasoning sound and logical?
   - Are data interpretations supported?
   - Is methodology scientifically rigorous?

3. Communication (0–100):
   - Is writing clear and well-organized?
   - Are figures/tables properly labeled?
   - Does it follow scientific writing conventions?

For each issue found, specify:
- Line/paragraph reference
- Type: critical/minor/suggestion
- Specific suggestion for improvement

Return JSON: {
  "understanding_score": N,
  "analysis_score": N,
  "communication_score": N,
  "issues": [{"line": "", "type": "", "suggestion": ""}]
}
```

### Peer Feedback Scoring Prompt

When a peer submits feedback, the system calls OpenAI with:

```
Score this peer feedback on a STEM student's work:

Original section: [author's text]
Peer feedback: [peer's feedback]

Rate on three dimensions (0–100 each):

1. Specificity: Is it detailed? Does it point to specific phrases/examples?
2. Constructiveness: Is it balanced? Does it offer actionable improvements?
3. Scientific Accuracy: Is the feedback technically correct?

Also provide:
- Summary: One sentence on the overall contribution
- Suggestions: How could this peer improve their feedback? (if score < 80)

Return JSON: {
  "specificity": N,
  "constructiveness": N,
  "scientific_accuracy": N,
  "overall_score": N,  # Average of three
  "summary": "",
  "suggestions": ""
}
```

---

## Deployment

### Local Development

```bash
python manage.py runserver
# Runs on http://127.0.0.1:8000 with auto-reload
```

### Production Deployment (Linux/Ubuntu)

#### Option 1: Systemd Service

Create `/etc/systemd/system/stemscribe.service`:

```ini
[Unit]
Description=StemScribe Django App
After=network.target

[Service]
Type=notify
User=django
WorkingDirectory=/home/django/stemscribe
ExecStart=/home/django/stemscribe/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    stemscribe.wsgi:application

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start stemscribe
sudo systemctl enable stemscribe  # Auto-start on boot
```

#### Option 2: Docker (Future)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py migrate
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stemscribe.wsgi:application"]
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name 159.65.240.114;

    location /static/ {
        alias /home/django/stemscribe/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Database Migration

On production server:

```bash
cd /home/django/stemscribe
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart stemscribe
```

---

## Development

### Project Structure

```
stemscribe/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # Local database
├── stemscribe/                  # Project configuration
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py                  # Production WSGI entry
├── core/                        # Main application
│   ├── models.py                # Database models (7 models)
│   ├── views.py                 # Views (30+ functions)
│   ├── urls.py                  # URL patterns
│   ├── templatetags/
│   │   └── stem_tags.py         # Custom template filters
│   ├── migrations/              # Database schema versions
│   │   ├── 0001_initial.py
│   │   ├── 0002_peershare*.py
│   │   ├── 0003_peerfeedback*.py
│   │   └── 0004_*.py
│   └── templates/core/
│       ├── base.html            # Base shell with CSS
│       ├── landing.html         # Homepage before login
│       ├── registration.html    # Sign up form
│       ├── student_base.html    # Student sidebar layout
│       ├── student_submit.html  # Upload/paste form
│       ├── student_analysis.html # Main report view
│       ├── student_version.html # Version history
│       ├── student_dashboard.html # Personal stats
│       ├── peer_feed.html       # Peer request browser
│       ├── peer_review.html     # Peer feedback form + AI review
│       ├── peer_activity.html   # Contribution dashboard
│       ├── edit_peer_feedback.html # Draft editing
│       ├── teacher_base.html    # Teacher sidebar layout
│       ├── teacher_dashboard.html
│       ├── teacher_student.html
│       ├── teacher_peer_overview.html
│       ├── teacher_rubric.html
│       ├── teacher_stats.html
│       └── teacher_upload.html
├── static/                      # CSS, JS, images
│   └── css/
│       └── style.css            # Design system (CSS variables)
└── venv/                        # Virtual environment
```

### Adding a New Feature

1. **Define model** in `core/models.py`
2. **Create migration:** `python manage.py makemigrations`
3. **Apply migration:** `python manage.py migrate`
4. **Write view** in `core/views.py`
5. **Add URL** to `core/urls.py`
6. **Create template** in `core/templates/core/`
7. **Test locally** before deployment

### Running Tests

```bash
python manage.py test core
python manage.py test core.tests.StudentViewTests
python manage.py test core.tests.PeerFeedbackTests
```

### Debugging

Enable verbose logging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console'], 'level': 'DEBUG'}},
}
```

Then tail logs while developing:

```bash
python manage.py runserver 2>&1 | grep -E "(ERROR|WARNING)"
```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. "no such table: core_peerfeedback"

**Solution:** Database schema mismatch. Run:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3. "Reverse for 'edit_peer_feedback' not found"

**Cause:** URL pattern missing from `urls.py`  
**Solution:** Ensure this line exists in `core/urls.py`:
```python
path('peer/edit/<int:feedback_id>/', views.edit_peer_feedback, name='edit_peer_feedback'),
```

#### 4. "CSRF verification failed"

**Solution:** Add to `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://159.65.240.114',
]
```

#### 5. "OpenAI API key not found"

**Solution:** Set environment variable:
```bash
export OPENAI_API_KEY=sk-your-key-here
# On Windows: set OPENAI_API_KEY=sk-your-key-here
```

Or add to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

#### 6. "Database is locked"

**Cause:** SQLite permissions issue on production  
**Solution:**
```bash
sudo chown django:django db.sqlite3
sudo chown django:django .
```

#### 7. "Peer feedback not scoring (AI feedback pending...)"

**Cause:** OpenAI API call failed silently  
**Solution:** Check server logs:
```bash
journalctl -u stemscribe -n 50 --no-pager
```

Ensure `OPENAI_API_KEY` is set on production server.

---

## Contributing

To contribute improvements:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with clear commit messages
4. Test thoroughly: `python manage.py test`
5. Push to GitHub and create pull request

---

## License

MIT License — See LICENSE file for details.

---

## Contact

Built for Imperial College London STEM education.  
Questions? Open an issue on GitHub or email: manishsharmatimilsina01@gmail.com

## Core Features

### Student Workflow

**1. Report Submission**
- Paste or upload report (.txt, .pdf, .docx)
- Edit inline before submission

**2. AI Analysis**
- OpenAI Claude API analyzes reports on Understanding / Analysis / Communication
- Colour-coded highlight report with inline issue marks
- Review and approve/reject each AI suggestion
- Approved changes create new document versions automatically

**3. Peer Feedback**
- Share specific sections (Introduction, Method, Results, Discussion, Conclusion, Custom) with peers
- Include optional question for reviewers
- Browse all open peer requests in feed
- Receive AI-scored feedback from peers
- Track contribution stats and leaderboard ranking

**4. Collaborative Editing**
- View feedback from peers and teacher in document context
- Edit and revise inline
- Download formatted report as file
- Version history with score progression

### Peer Review System

**Peer Contribution Workflow:**
1. **Browse requests** — View all shared sections from classmates
2. **Give feedback** — Submit initial feedback draft
3. **AI review** — Claude scores feedback on:
   - Specificity (is it detailed and specific?)
   - Constructiveness (is it balanced and helpful?)
   - Scientific accuracy (is it technically correct?)
   - Overall contribution score (0–100)
4. **Edit & improve** — Review AI suggestions and revise feedback
5. **Submit** — Send final feedback to the student

**Peer Activity Dashboard:**
- View feedback you've given (with AI scores and suggestions)
- View feedback you've received (with contributor scores)
- Edit draft feedback before it reaches the student
- Track your average contribution score

### Teacher Dashboard

**Peer Oversight:**
- Class leaderboard showing peer contribution scores
- Complete activity log of all peer feedback
- Monitor peer feedback quality and engagement
- View individual student contribution stats

**Student Management:**
- Per-student view of documents, versions, and feedback
- Add teacher comments on student work
- View peer feedback received by each student
- Track class statistics (Understanding / Analysis / Communication scores)
- Custom rubric management (add, edit, delete criteria per pillar)

## Models & Database

```
UserProfile          — User role (Student/Teacher) + class assignment
Document             — Student report container
DocumentVersion      — Individual versions with AI scores
RubricCriterion      — Teacher-defined grading criteria
PeerShareRequest     — Section shared for peer review
PeerFeedback         — Peer feedback with draft/submitted status + AI scoring
TeacherComment       — Teacher annotations on documents
```

## Architecture

```
stemscribe/
├── manage.py
├── requirements.txt
├── stemscribe/
│   ├── settings.py
│   └── urls.py
└── core/
    ├── models.py
    ├── views.py          # 30+ views for student/peer/teacher flows
    ├── urls.py
    ├── templatetags/
    │   └── stem_tags.py  # Report formatting filters
    └── templates/core/
        ├── landing.html
        ├── registration.html
        ├── student_base.html
        ├── student_submit.html
        ├── student_analysis.html
        ├── student_version.html
        ├── student_dashboard.html
        ├── peer_feed.html
        ├── peer_review.html
        ├── peer_activity.html
        ├── edit_peer_feedback.html
        ├── teacher_base.html
        ├── teacher_dashboard.html
        ├── teacher_stats.html
        ├── teacher_student.html
        ├── teacher_rubric.html
        ├── teacher_upload.html
        ├── teacher_peer_overview.html
        └── [more templates]
```

## API Integration

**OpenAI Claude:**
- Report analysis (Understanding / Analysis / Communication scores)
- Peer feedback quality scoring (Specificity / Constructiveness / Scientific Accuracy)
- AI suggestions to improve peer feedback
- Uses Python's built-in `urllib` — no extra dependencies

Set `OPENAI_API_KEY` as environment variable. Required for full functionality.
