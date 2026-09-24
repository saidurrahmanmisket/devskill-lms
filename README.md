# DEVSKILL LMS

> **A modern, full-featured Learning Management System built with Django 6 — designed for academic institutions and online education platforms.**

---

## Overview

DEVSKILL LMS is a multi-role academic platform with a rich frontend catalog and a premium internal dashboard for admins, faculty, and students. It supports course authoring with multi-media content (video, audio, PDF, text, image, external links), assignment management, grading, and a public course catalog.

---

## Screenshots

| Public Catalog | Faculty Dashboard | Curriculum Builder |
|---|---|---|
| Course grid with hover effects | Analytics + KPI cards | Module + Lesson AJAX editor |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.1 |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| Frontend | Vanilla HTML/CSS + JavaScript (no framework) |
| File Handling | Pillow 12 (ImageField), ReportLab (PDF export) |
| Markdown | Python-Markdown 3.10 |
| Auth | Custom User model with role-based access |
| Icons | Font Awesome 6.5 |
| Fonts | Plus Jakarta Sans (Google Fonts) |

---

## Features

### Role-Based Access Control
- **Admin** — Full platform governance, user management, audit logs, CSV bulk import
- **Faculty (Instructor)** — Course authoring, curriculum building, gradebook, assignment dispatch
- **Student** — Course enrollment, lesson viewing, assignment submission, grade tracking

### Public Frontend
- Hero landing page with animated statistics
- Course catalog with 3-column grid, hover play icon, search & department filter
- Course detail page with syllabus, module list, and enrollment CTA
- Mentors/instructors directory page
- Fully responsive design with teal/orange design system

### Admin Dashboard (`/admin-portal/`)
- Analytics hero card with live enrollment + evaluation data
- 4 KPI stat cards (students, faculty, courses, submissions)
- Enrollment growth area chart + Department donut chart (ApexCharts)
- User directory table with one-click activate/deactivate
- Audit trail timeline
- CSV bulk user import

### Faculty Dashboard (`/faculty/`)
- Teaching analytics hero card
- 4 KPI cards (students mentored, active courses, pending grades, graded count)
- My Courses table with publish toggle
- Pending grading queue
- Master Gradebook

### Course Authoring Studio
- Premium 2-column course creation form (inside dashboard — no public redirect)
- Live thumbnail preview with drag & drop
- Markdown syllabus editor
- Instant publish / draft toggle

### Curriculum Builder (AJAX)
- Two-panel layout: curriculum tree (left) + add panel (right)
- Add/delete modules and lessons **without page reload**
- 6 lesson content types:
  - **Text / Markdown** — Rich formatted content
  - **Video** — Upload `.mp4` / `.webm` (max 50 MB)
  - **Audio** — Upload `.mp3` / `.wav` / `.ogg` (max 50 MB)
  - **PDF** — Upload `.pdf` documents
  - **Image** — Upload `.png` / `.jpg` / `.gif`
  - **External Link** — YouTube, Vimeo, articles
- Estimated duration field per lesson
- Toast notifications for all actions
- Upload progress indicator

### Student Workspace (`/student/`)
- Personal learning hub with enrolled courses
- Course viewer with module/lesson sidebar
- Assignment submission with file upload
- Grades & feedback page

---

## Project Structure

```
devskill-lms/
├── accounts/           # Custom User model, auth views, decorators
│   ├── models.py       # User with Role (ADMIN, INSTRUCTOR, STUDENT)
│   ├── views.py        # Login, register, demo login, logout
│   └── decorators.py   # @role_required decorator
├── lms/                # Core LMS application
│   ├── models.py       # Course, Module, Lesson, Assignment, Submission, AuditLog
│   ├── views_public.py # Public catalog, course detail, mentors
│   ├── views_faculty.py# Dashboard, course CRUD, curriculum builder, AJAX endpoints
│   ├── views_student.py# Dashboard, course viewer, assignment submit
│   ├── views_admin.py  # Admin dashboard, user management, audit logs
│   └── urls.py         # All URL routing
├── templates/
│   ├── base.html       # Public layout (navbar + footer)
│   ├── admin/
│   │   └── base_admin.html  # Sidebar dashboard layout
│   ├── public/         # index, catalog, course_detail, mentors
│   ├── faculty/        # dashboard, curriculum_builder, course_create, gradebook
│   ├── student/        # dashboard, my_courses, course_detail, grades
│   └── auth/           # login, register
├── static/
│   ├── css/main.css    # Global design system
│   ├── js/main.js
│   └── images/         # Course thumbnails, mentor photos, hero images
├── univlms/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
└── manage.py
```

---

## Installation

### Prerequisites
- Python 3.10+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/saidurrahmanmisket/devskill-lms.git
cd devskill-lms

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Seed demo data (optional but recommended)
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**

---

## Demo Accounts

The seed command creates the following demo users:

| Role | Quick Login URL |
|---|---|
| Admin | http://127.0.0.1:8000/accounts/demo-login/admin/ |
| Faculty | http://127.0.0.1:8000/accounts/demo-login/instructor/ |
| Student | http://127.0.0.1:8000/accounts/demo-login/student/ |

> The navigation bar also has **Admin / Faculty / Student** quick-switch buttons for convenience during development.

---

## Key URLs

| URL | Description |
|---|---|
| `/` | Public home / landing page |
| `/courses/` | Course catalog with search & filter |
| `/mentors/` | Mentor directory |
| `/admin-portal/dashboard/` | Admin analytics dashboard |
| `/faculty/dashboard/` | Faculty instruction hub |
| `/faculty/courses/create/` | Course authoring studio |
| `/faculty/courses/<id>/curriculum/` | Curriculum builder |
| `/faculty/my-courses/` | Faculty course list |
| `/faculty/gradebook/` | Master gradebook |
| `/student/dashboard/` | Student workspace |
| `/student/my-courses/` | Enrolled courses |

---

## Data Models

```
User (accounts)
  └── role: ADMIN | INSTRUCTOR | STUDENT

Course
  ├── thumbnail (ImageField)
  ├── description
  ├── syllabus_outline (Markdown)
  └── instructor → User

  Module (belongs to Course)
    └── Lesson (belongs to Module)
          ├── lesson_type: TEXT | VIDEO | AUDIO | PDF | IMAGE | LINK
          ├── content_markdown
          ├── media_file (up to 50 MB)
          ├── external_url
          └── duration_minutes

Enrollment (Student ↔ Course)

Assignment (belongs to Course)
  └── Submission (Student → Assignment)
        ├── file (PDF/ZIP/DOCX up to 25 MB)
        ├── score
        └── feedback_markdown

AuditLog (actor, action_type, target_entity, timestamp)
```

---

## Environment & Configuration

Create a `.env` file (not committed) for production settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the **MIT License**.

---

*Built with Django 6 · Designed with a teal & orange design system · Font Awesome 6.5 icons*
