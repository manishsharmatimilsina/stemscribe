# StemScribe — AI-Guided STEM Writing Platform

A Django web app for AI-powered peer feedback on STEM lab reports.

## Quick Start

```bash
# 1. Install Django
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Set your Anthropic API key (optional — falls back to demo data)
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 4. Start the server
python manage.py runserver
```

Then open http://127.0.0.1:8000

## Demo Login Credentials

**Student:** student@imperial.ac.uk / demo1234
**Teacher:** teacher@imperial.ac.uk / demo1234

(Any email/password combination will work — accounts are auto-created on first login)

## Features

### Student
- Landing page with drag slider before/after comparison
- Submit reports via paste or file upload (.txt, .pdf, .docx)
- AI analysis via Claude API (falls back to demo data if no key set)
- Colour-coded highlighted report with clickable issue marks
- Feedback panel: approve/reject each AI suggestion
- Approving creates a new document version automatically
- Version history with side-by-side score panel
- Personal dashboard: score progression bars, classroom impact chain, collaborator level bar
- Sidebar with expandable document tree (Open / Version History / Dashboard)

### Teacher
- Class dashboard with Statistics / Feedback tabs
- Flags for low-participation and struggling students
- Top collaborators leaderboard
- Per-student view: documents, peer feedback outputs, score breakdown
- Class statistics table with Understanding / Analysis / Communication scores
- Rubric editor: add, edit, delete criteria per pillar (modal interface)
- Upload documents page

## Architecture

```
stemscribe/
├── manage.py
├── requirements.txt
├── stemscribe/          # Django project settings
│   ├── settings.py
│   └── urls.py
└── core/                # Main app
    ├── models.py        # UserProfile, Document, DocumentVersion, RubricCriterion, PeerEdit
    ├── views.py         # All student + teacher views + Claude API call
    ├── urls.py
    ├── templatetags/
    │   └── stem_tags.py # highlight_report filter
    └── templates/core/
        ├── base.html           # Shell with sidebar
        ├── landing.html        # Before/after drag slider + login
        ├── student_base.html   # Student sidebar nav
        ├── student_submit.html
        ├── student_analysis.html
        ├── student_version.html
        ├── student_dashboard.html
        ├── student_howto.html
        ├── teacher_base.html
        ├── teacher_dashboard.html
        ├── teacher_stats.html
        ├── teacher_student.html
        ├── teacher_rubric.html
        ├── teacher_upload.html
        └── teacher_feedback.html
```

## API Integration

The app calls `https://api.anthropic.com/v1/messages` using only Python's built-in `urllib` — no extra packages needed. Set `ANTHROPIC_API_KEY` as an environment variable. Without a key, the app uses realistic demo data automatically.
