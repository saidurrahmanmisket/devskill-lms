"""
add_aos.py  --  Injects data-aos attributes into DevSkill LMS templates.
Run from the project root: python scripts/add_aos.py
"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def patch(filepath, pairs):
    full = os.path.join(BASE, filepath)
    with open(full, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in pairs:
        content = content.replace(old, new, 1)
    if content != original:
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK]  {filepath}')
    else:
        print(f'[--]  {filepath}  (no changes)')


# ── PUBLIC: index.html ───────────────────────────────────────────
patch('templates/public/index.html', [
    ('<div class="dev-sticker-salmon">',
     '<div class="dev-sticker-salmon" data-aos="fade-down">'),
    ('<div class="dev-pill-solid-teal">About Us</div>',
     '<div class="dev-pill-solid-teal" data-aos="fade-up">About Us</div>'),
    ('<h2 class="dev-about-heading">',
     '<h2 class="dev-about-heading" data-aos="fade-up" data-aos-delay="100">'),
    ('<div class="dev-stats-grid">',
     '<div class="dev-stats-grid" data-aos="fade-up" data-aos-delay="200">'),
    ('<div class="dev-sticker-orange">Our Course</div>',
     '<div class="dev-sticker-orange" data-aos="fade-up">Our Course</div>'),
    ('<h2 class="dev-section-title">Explore Our Course</h2>',
     '<h2 class="dev-section-title" data-aos="fade-up" data-aos-delay="80">Explore Our Course</h2>'),
    ('<div class="dev-courses-grid">',
     '<div class="dev-courses-grid" data-aos="fade-up" data-aos-delay="150">'),
    ('<div class="dev-sticker-orange">Categories</div>',
     '<div class="dev-sticker-orange" data-aos="fade-up">Categories</div>'),
    ('<div class="dev-cats-grid">',
     '<div class="dev-cats-grid" data-aos="fade-up" data-aos-delay="120">'),
    ('<div class="dev-growth-left">',
     '<div class="dev-growth-left" data-aos="fade-right" data-aos-delay="50">'),
    ('<div class="dev-growth-right">',
     '<div class="dev-growth-right" data-aos="fade-left" data-aos-delay="100">'),
    ('<div class="dev-testimonial-card">',
     '<div class="dev-testimonial-card" data-aos="zoom-in" data-aos-delay="100">'),
    ('<div class="dev-faq-grid">',
     '<div class="dev-faq-grid" data-aos="fade-up">'),
    ('<div class="dev-dual-cards">',
     '<div class="dev-dual-cards" data-aos="fade-up" data-aos-delay="100">'),
])

# ── STUDENT dashboard ────────────────────────────────────────────
patch('templates/student/dashboard.html', [
    ('class="row g-4 mb-4"',
     'class="row g-4 mb-4" data-aos="fade-up"'),
])

# ── STUDENT my_courses ───────────────────────────────────────────
patch('templates/student/my_courses.html', [
    ('class="row g-4"',
     'class="row g-4" data-aos="fade-up" data-aos-delay="80"'),
])

# ── STUDENT grades ───────────────────────────────────────────────
patch('templates/student/grades.html', [
    ('<table ',
     '<table data-aos="fade-up" '),
])

# ── FACULTY dashboard ────────────────────────────────────────────
patch('templates/faculty/dashboard.html', [
    ('class="row g-4 mb-4"',
     'class="row g-4 mb-4" data-aos="fade-up"'),
])

# ── FACULTY my_courses ───────────────────────────────────────────
patch('templates/faculty/my_courses.html', [
    ('class="row g-4"',
     'class="row g-4" data-aos="fade-up" data-aos-delay="80"'),
])

# ── FACULTY gradebook ────────────────────────────────────────────
patch('templates/faculty/gradebook.html', [
    ('<table ',
     '<table data-aos="fade-up" '),
])

# ── ADMIN dashboard ──────────────────────────────────────────────
patch('templates/admin/dashboard.html', [
    ('class="row g-4 mb-4"',
     'class="row g-4 mb-4" data-aos="fade-up"'),
])

# ── ADMIN users ──────────────────────────────────────────────────
patch('templates/admin/users.html', [
    ('<table ',
     '<table data-aos="fade-up" '),
])

# ── ADMIN audit_logs ─────────────────────────────────────────────
patch('templates/admin/audit_logs.html', [
    ('<table ',
     '<table data-aos="fade-up" '),
])

print('\nAll done!')
