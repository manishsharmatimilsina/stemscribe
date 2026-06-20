# StemScribe: AI-Guided Collaboration for STEM Writing

**Structured edits, real impact.**

---

## Project Overview & Team

**StemScribe** is an AI-powered peer feedback system designed to transform how feedback works in STEM education. Built as a full-stack web platform, it enables students to receive structured, actionable feedback while maintaining human oversight over AI recommendations.

### Team Members

| Name | Year/Level | Role | Contribution |
|------|-----------|------|--------------|
| **Aimma Shahzad** | 4th Year, Medicine | Co-Founder | Product design, user research, feedback workflows |
| **Akshara Suresh** | 2nd Year, Medicine | Co-Founder | Peer review system, platform testing |
| **Manish Sharma Timilsina** | Postgraduate, Chemical Engineering | Technical Lead | Full-stack development, API integration, deployment |

---

## Grand Challenge Addressed

**AI-Powered Peer Feedback Coach for STEM Outputs**

StemScribe tackles the critical gap in STEM education: students receive feedback that is unstructured, inconsistent, and difficult to apply—leading to superficial improvements and passive learning. Simultaneously, emerging AI tools risk over-automation, where students blindly accept suggestions without understanding them.

StemScribe solves this by combining AI-driven structure with human control, ensuring feedback is actionable, trustworthy, and educational.

---

## Problem Statement & Solution Overview

### The Problem

Feedback is essential for learning, but in STEM education it often breaks down in practice:

- **Unstructured:** Feedback lacks clear direction or alignment with learning objectives
- **Inconsistent:** Quality varies across peers and instructors
- **Hard to apply:** Students don't know how to translate feedback into concrete revisions
- **Over-automated:** AI tools encourage passive acceptance without genuine understanding

### The Solution: StemScribe

StemScribe is a human–AI collaborative platform that transforms feedback through four key mechanisms:

1. **Structured Feedback** – AI organizes feedback into clear, rubric-aligned categories (clarity, scientific accuracy, reasoning)
2. **Quality Assurance** – AI evaluates peer feedback for specificity, constructiveness, and correctness before delivery
3. **Human-in-the-Loop** – Students actively review, interpret, and decide how to apply feedback, preventing over-reliance on AI
4. **Learning Tracking** – Version control allows students and educators to see how work evolves, visualizing genuine learning progress

---

## Technology Stack & Architecture

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python with Django |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **AI Engine** | OpenAI API (Claude) |
| **Deployment** | Gunicorn, Nginx, Linux/Ubuntu |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Users: Students | Peers | Teachers                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Frontend Layer                                              │
│  • Submission Interface   • Feedback Review   • Dashboards   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Django Backend                                              │
│  • Authentication   • Workflow Management   • Feedback Routing │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Database Layer                                              │
│  • Documents   • Feedback   • Versions   • Rubrics           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  AI Layer                                                    │
│  • Writing Analysis   • Peer Feedback QA   • Suggestions     │
│  OpenAI API: Claude                                          │
└─────────────────────────────────────────────────────────────┘
```

### Core Database Models

```
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

```

**Key Models:**
- **UserProfile:** Connects users to roles (Student/Teacher) and class assignments
- **Document:** Container for all versions of a student's report
- **DocumentVersion:** Immutable historical record with AI scores and issue tracking
- **PeerShareRequest:** Manages which document sections are shared for peer review
- **PeerFeedback:** Peer feedback with draft/submitted status and AI quality scores
- **RubricCriterion:** Teacher-defined grading criteria per pillar
- **TeacherComment:** Teacher annotations on student documents


## Installation & Setup Instructions

### System Requirements

- **Python:** 3.8 or higher
- **Database:** SQLite (included) or PostgreSQL for production
- **OS:** macOS, Linux, Windows (WSL recommended)
- **Git:** For cloning the repository

### Step 1: Clone the Repository

```bash
git clone https://github.com/manishsharmatimilsina/stemscribe.git
cd stemscribe/stemscribe
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 5: Initialize Database

```bash
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Access the admin panel at `http://localhost:8000/admin`

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Student | student@imperial.ac.uk | demo1234 |
| Teacher | teacher@imperial.ac.uk | demo1234 |

**Note:** Registration creates accounts automatically. Both students and teachers register and select their role during signup.

---

## Usage Guide

### 1. Student Workflow: Report Submission & Analysis

#### Submission
- **Entry Point:** `/student/submit/`
- **Methods:** Paste text, upload (.txt, .pdf, .docx), or link to external document
- **Max file size:** 5MB

#### AI Analysis & Feedback
1. Report submitted → Django extracts text (handles PDF/DOCX conversion)
2. OpenAI  analyzes on three dimensions:
   - **Understanding:** Concept comprehension, definitions, theory grounding
   - **Analysis:** Critical thinking, data interpretation, methodology soundness
   - **Communication:** Clarity, organization, writing conventions
3. AI returns:
   - Overall score (0–100) for each dimension
   - Detailed issues with line numbers and specific suggestions
   - Color-coded highlights (red=critical, yellow=minor, green=suggestions)

     <img width="2822" height="1534" alt="image" src="https://github.com/user-attachments/assets/96e3d8cc-4e2e-41e9-9968-aa27da787286" />

#### Feedback Review
- Click issues to expand details
- **Approve:** Applies suggestion, creates new DocumentVersion
- **Reject:** Dismisses issue without action
- **Edit:** Modify suggestion before approving


#### Version Tracking
- Browse version history showing score progression
- Compare versions side-by-side
- See full edit timeline with timestamps

<img width="2848" height="1508" alt="image" src="https://github.com/user-attachments/assets/9da85a0e-8e7b-4df7-a933-84535a8cd1d7" />

---

### 2. Peer Review System

**Core Concept:** Quality-assured peer feedback through AI review before reaching the student.

#### Step-by-Step Workflow

**Step 1: Share a Section for Review**
- **Entry Point:** `/student/analysis/<doc_id>/share-section/`
- Select section type: Introduction, Method, Results, Discussion, Conclusion, or Custom
- Optionally include a guiding question for reviewers
- Creates `PeerShareRequest` with `is_open=True`

  <img width="2398" height="1468" alt="image" src="https://github.com/user-attachments/assets/f871c3d3-8366-40dd-bb90-5e24273afe04" />


**Step 2: Peers Discover Requests**
- **Entry Point:** `/peer/feed/`
- Browse all open peer requests from classmates
- Filter by section type or class



**Step 3: Peer Submits Initial Feedback**
- **Entry Point:** `/peer/review/<share_id>/`
- Read shared section and optional author question
- Type feedback in textarea
- Click "Save & review with AI"
- Creates `PeerFeedback` record in draft state

<img width="2118" height="1546" alt="image" src="https://github.com/user-attachments/assets/b0e257a5-eed9-4976-a5e7-2dda4e79b04c" />


**Step 4: AI Quality Scoring**
Backend analyzes peer feedback on:
- **Specificity (0–100):** Is it detailed? Does it point to specific phrases?
- **Constructiveness (0–100):** Is it balanced and actionable?
- **Scientific Accuracy (0–100):** Is it technically correct?

Overall `ai_contribution_score` calculated as average of three dimensions.

**Step 5: Peer Reviews AI Suggestions & Edits**
- Peer sees draft feedback, AI scores, and improvement suggestions
- **Edit feedback:** `/peer/edit/<feedback_id>/`
- Revise based on AI suggestions
- Click "Save & re-score" for new AI scoring
- Process repeats until satisfied

**Step 6: Submit Final Feedback**
- Click "Send to student"
- Sets `is_submitted=True`
- Feedback now appears in student's document view (read-only)
- Peer can no longer edit once submitted

  <img width="1564" height="1332" alt="image" src="https://github.com/user-attachments/assets/a1365eaa-58c2-4247-9175-9df5e90f7285" />


#### Peer Activity Dashboard
- **Entry Point:** `/peer/activity/`
- View all feedback given (with AI scores and edit links for drafts)
- View feedback received on your shared sections
- See your average contribution score
- Public leaderboard incentivizes quality contributions

<img width="2030" height="1496" alt="image" src="https://github.com/user-attachments/assets/286f46d6-0249-4613-a741-23a561d4fa80" />

---

### 3. Teacher Dashboard & Oversight

#### Dashboard Overview
- **Entry Point:** `/teacher/dashboard/`
- Class-wide statistics (average scores, engagement metrics)
- Student list with performance flags (red=struggling, green=top performers)

#### Per-Student Management
- **Entry Point:** `/teacher/student/<student_id>/`
- View all documents and versions for a student
- See all peer feedback they've received
- Add/edit/delete teacher comments
- Review score breakdown by dimension

#### Peer Feedback Oversight
- **Entry Point:** `/teacher/peer-overview/`
- Class leaderboard by peer contribution score
- Activity log with timestamps, reviewers, sections, quality scores
- Identify top peer reviewers and disengaged students

  <img width="2868" height="1446" alt="image" src="https://github.com/user-attachments/assets/55f67f29-55ba-4616-8632-5119546faf4c" />


#### Custom Rubric Management
- **Entry Point:** `/teacher/rubric/`
- Add/edit/delete criteria under each pillar:
  - Understanding (conceptual grasp, definitions, theory)
  - Analysis (critical thinking, data interpretation)
  - Communication (clarity, organization, grammar)
- Criteria feed AI analysis prompts (customizable per class)

  


#### Bulk Document Upload
- **Entry Point:** `/teacher/upload/`
- Upload multiple student documents via CSV
- Useful for batch-loading lab reports at semester start

---

### 4. Collaborative Document View

- **Entry Point:** `/student/analysis/<doc_id>/`
- Full report with preserved formatting
- Inline feedback panels from AI and peers
- View teacher comments (teachers can edit/delete)
- **Actions:** Edit inline, download as PDF/DOCX, view version history

---


## API Endpoints Reference

### Student Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/student/dashboard/` | Personal stats and quick links |
| GET/POST | `/student/submit/` | Upload or paste new report |
| GET | `/student/analysis/<doc_id>/` | View report with feedback |
| POST | `/student/analysis/<doc_id>/save-revision/` | Save inline edits |
| POST | `/student/analysis/<doc_id>/download/` | Export report as file |
| GET/POST | `/student/analysis/<doc_id>/share-section/` | Share section for peer review |
| GET/POST | `/student/version/<doc_id>/` | View and compare versions |

### Peer Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/peer/feed/` | Browse open peer requests |
| GET/POST | `/peer/review/<share_id>/` | Submit feedback |
| POST | `/peer/review/<share_id>/?action=submit` | Submit drafted feedback |
| GET/POST | `/peer/edit/<feedback_id>/` | Edit drafted feedback |
| POST | `/peer/close/<share_id>/` | Author closes peer request |
| GET | `/peer/activity/` | View contribution stats |

### Teacher Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/teacher/dashboard/` | Class statistics and student flags |
| GET | `/teacher/student/<student_id>/` | Per-student overview |
| GET | `/teacher/peer-overview/` | Peer feedback leaderboard |
| GET/POST | `/teacher/rubric/` | Manage custom criteria |
| GET/POST | `/teacher/upload/` | Bulk upload documents |

### Authentication Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Landing page |
| GET/POST | `/register/` | New account creation |
| GET/POST | `/login/` | Login |
| POST | `/logout/` | Logout |

---

## Links

### Live Deployment

🌐 **[Visit StemScribe](http://159.65.240.114:1005/)**

### Demo Video

📹 **[View Demo Video]** *(Link to be added)*

---

## Team Member Details & Contribution

### Aimma Shahzad (4th Year, Medicine)
- **Role:** Co-Founder & Product Designer
- **Contributions:**
  - Product vision and strategy
  - User research and workflow design
  - Peer feedback system architecture
  - Stakeholder management and user testing

### Akshara Suresh (2nd Year, Medicine)
- **Role:** Co-Founder & QA Lead
- **Contributions:**
  - Peer review system development
  - Platform testing and validation
  - User feedback integration
  - Documentation and user guides

### Manish Sharma Timilsina (Postgraduate, Chemical Engineering)
- **Role:** Technical Lead & Full-Stack Developer
- **Contributions:**
  - Full-stack architecture design
  - Django backend development
  - Frontend implementation
  - OpenAI API integration
  - Database schema and deployment
  - DevOps and server configuration

---

## License Information

This project is developed for **Imperial College London STEM education** purposes.

### Project License

The overall project license should be defined by the project maintainers. The third-party technologies used in this project are governed by their own licenses, listed below.

### Third-Party Licenses

| Technology | License | License Type |
|---|---|---|
| Python | Python Software Foundation License (PSF) | Permissive; free for commercial use |
| Django | BSD 3-Clause License | Permissive; free for commercial use |
| PostgreSQL | PostgreSQL License | Permissive; free for commercial use; no copyleft obligations |
| OpenAI API | Commercial / Proprietary | Pay-per-use API service governed by OpenAI’s Terms of Service |

### Notes

- Python, Django, and PostgreSQL are open-source technologies with permissive licenses.
- The OpenAI API is a commercial service and is subject to OpenAI’s pricing, usage policies, and Terms of Service.
- This project does not redistribute OpenAI models or proprietary OpenAI software.
- Users and maintainers should ensure compliance with all applicable third-party license terms when deploying, modifying, or distributing this project.
---

## Development & Contributing

### Project Structure
```
stemscribe/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # Local database
├── stemscribe/                  # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                        # Main application
│   ├── models.py                # 7 core models
│   ├── views.py                 # 30+ view functions
│   ├── urls.py
│   ├── migrations/              # Database schema versions
│   └── templates/core/          # HTML templates
├── static/                      # CSS, JS, images
└── venv/                        # Virtual environment
```

### Adding a Feature

1. Define model in `core/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Write view in `core/views.py`
5. Add URL to `core/urls.py`
6. Create template in `core/templates/core/`
7. Test locally before deployment

### Running Tests

```bash
python manage.py test core
python manage.py test core.tests.StudentViewTests
python manage.py test core.tests.PeerFeedbackTests
```

### Debugging

Enable verbose logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console'], 'level': 'DEBUG'}},
}
```

Then tail logs:
```bash
python manage.py runserver 2>&1 | grep -E "(ERROR|WARNING)"
```

### Production Deployment

**Systemd Service:**
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
sudo systemctl enable stemscribe
```

**Nginx Configuration:**
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

### Contributing

To contribute improvements:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with clear commit messages
4. Test thoroughly: `python manage.py test`
5. Push to GitHub and create pull request

---

## Contact & Support

Built for **Imperial College London** STEM education.

**Questions?** Open an issue on GitHub or email:
📧 **m.sharma-timilsina25@imperial.ac.uk**

---

## Acknowledgments

Special thanks to Imperial College London for supporting this project and the STEM student community for invaluable feedback during development.
