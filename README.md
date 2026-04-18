# StemScribe — AI-Guided STEM Writing Platform

A Django web app for AI-powered feedback on STEM lab reports. Students submit reports, receive AI analysis, get peer feedback, and collaborate through a structured review system with teacher oversight.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Set your OpenAI API key (required for AI feedback)
export OPENAI_API_KEY=sk-your-key-here

# 4. Start the server
python manage.py runserver
```

Then open http://127.0.0.1:8000

## Registration & Login

Users register with email and password. Roles (Student/Teacher) are assigned during registration.

**Demo Accounts:**
- **Student:** student@imperial.ac.uk / demo1234
- **Teacher:** teacher@imperial.ac.uk / demo1234

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
