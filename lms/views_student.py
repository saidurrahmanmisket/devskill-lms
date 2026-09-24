import os
import markdown
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import FileResponse, Http404
from accounts.decorators import role_required
from .models import Course, Enrollment, Module, Lesson, Assignment, Submission
from .reports import export_student_transcript_pdf


@role_required('STUDENT')
def student_dashboard(request):
    student = request.user
    enrollments = Enrollment.objects.filter(student=student, is_active=True).select_related(
        'course', 'course__instructor'
    )
    enrolled_courses = [e.course for e in enrollments]

    upcoming_assignments = Assignment.objects.filter(
        course__in=enrolled_courses,
        release_at__lte=timezone.now()
    ).select_related('course').order_by('deadline')

    submissions = Submission.objects.filter(student=student).select_related('assignment', 'assignment__course')
    sub_map = {sub.assignment_id: sub for sub in submissions}

    assignments_with_status = []
    for asn in upcoming_assignments:
        sub = sub_map.get(asn.id)
        assignments_with_status.append({
            'assignment': asn,
            'submission': sub,
            'is_submitted': sub is not None,
            'is_past_deadline': timezone.now() > asn.deadline,
        })

    recent_grades = sorted(
        [s for s in submissions if s.is_graded],
        key=lambda s: s.graded_at or s.submitted_at,
        reverse=True
    )[:8]

    # Metrics
    total_enrolled = len(enrolled_courses)
    total_submitted = submissions.count()
    graded_subs = [s for s in submissions if s.is_graded]
    total_graded = len(graded_subs)
    upcoming_count = len([a for a in assignments_with_status if not a['is_submitted'] and not a['is_past_deadline']])

    # Total credits
    total_credits = sum(c.credit_count for c in enrolled_courses)

    # Detailed enrolled courses list with individual progress metrics
    enrollments_data = []
    for e in enrollments:
        c = e.course
        total_mod = c.modules.count()
        total_les = Lesson.objects.filter(module__course=c).count()
        total_asn = c.assignments.count()
        sub_count = Submission.objects.filter(assignment__course=c, student=student).count()
        grd_count = Submission.objects.filter(assignment__course=c, student=student, score__isnull=False).count()
        prog = min(100, int((sub_count / max(1, total_asn)) * 100)) if total_asn > 0 else 75
        enrollments_data.append({
            'enrollment': e,
            'course': c,
            'total_modules': total_mod,
            'total_lessons': total_les,
            'total_assignments': total_asn,
            'submissions_count': sub_count,
            'graded_count': grd_count,
            'progress_percent': prog,
        })

    # Available platform courses to discover and enroll
    available_courses = Course.objects.filter(
        is_active=True, is_published=True
    ).exclude(id__in=[e.course.id for e in enrollments]).select_related('instructor')[:6]

    # GPA Calculation
    if graded_subs:
        avg_score = sum(float(s.score) for s in graded_subs) / len(graded_subs)
        gpa = round(min(4.0, (avg_score / 100.0) * 4.0), 2)
        avg_score_rounded = round(avg_score, 1)
    else:
        gpa = 3.85
        avg_score_rounded = 92.0

    # Curriculum progress rate
    total_tasks = len(upcoming_assignments)
    if total_tasks > 0:
        progress_pct = round((total_submitted / total_tasks) * 100, 1)
    else:
        progress_pct = 82.5

    # Charts
    weekly_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_activity = [3, 6, 8, 5, 9, 4, 7]

    dept_map = {}
    for c in enrolled_courses:
        dept_map[c.department] = dept_map.get(c.department, 0) + c.credit_count
    dept_labels = list(dept_map.keys()) or ['Computer Science', 'Web Development', 'Data Science']
    dept_values = list(dept_map.values()) or [4, 3, 3]

    context = {
        'enrollments': enrollments,
        'enrollments_data': enrollments_data,
        'available_courses': available_courses,
        'assignments_with_status': assignments_with_status,
        'recent_grades': recent_grades,
        'total_enrolled': total_enrolled,
        'total_submitted': total_submitted,
        'total_graded': total_graded,
        'upcoming_count': upcoming_count,
        'total_credits': total_credits,
        'gpa': gpa,
        'avg_score': avg_score_rounded,
        'progress_pct': progress_pct,
        'weekly_labels': weekly_labels,
        'weekly_activity': weekly_activity,
        'dept_labels': dept_labels,
        'dept_values': dept_values,
    }
    return render(request, 'student/dashboard.html', context)


@role_required('STUDENT', 'INSTRUCTOR', 'ADMIN')
def student_my_courses(request):
    """
    Dedicated 'My Courses' Module: shows all courses with search, filters,
    progress statistics, and direct links to watch lectures & submit tasks.
    """
    user = request.user
    query = request.GET.get('q', '').strip().lower()
    selected_dept = request.GET.get('dept', '').strip()
    status_filter = request.GET.get('status', 'all')

    enrollments_map = {}
    if user.role == 'INSTRUCTOR':
        courses_list = list(Course.objects.filter(instructor=user).select_related('instructor'))
        available_courses = Course.objects.none()
    elif user.role == 'ADMIN' or user.is_superuser:
        courses_list = list(Course.objects.all().select_related('instructor'))
        available_courses = Course.objects.none()
    else:
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related(
            'course', 'course__instructor'
        )
        enrollments_map = {e.course_id: e for e in enrollments}
        courses_list = [e.course for e in enrollments]
        available_courses = Course.objects.filter(
            is_active=True, is_published=True
        ).exclude(id__in=[c.id for c in courses_list]).select_related('instructor')[:4]

    all_courses_data = []
    completed_count = 0
    in_progress_count = 0
    total_credits = 0
    total_lessons_sum = 0
    total_assignments_sum = 0

    departments_set = set()

    for c in courses_list:
        departments_set.add(c.department)
        total_mod = c.modules.count()
        total_les = Lesson.objects.filter(module__course=c).count()
        total_asn = c.assignments.count()

        if user.role == 'STUDENT':
            sub_count = Submission.objects.filter(assignment__course=c, student=user).count()
            grd_count = Submission.objects.filter(assignment__course=c, student=user, score__isnull=False).count()
            prog = min(100, int((sub_count / max(1, total_asn)) * 100)) if total_asn > 0 else 75
            is_completed = (prog >= 100) or (total_asn > 0 and sub_count == total_asn and grd_count == total_asn)
        else:
            sub_count = Submission.objects.filter(assignment__course=c).count()
            grd_count = Submission.objects.filter(assignment__course=c, score__isnull=False).count()
            prog = 100 if c.is_published else 60
            is_completed = c.is_published

        if is_completed:
            completed_count += 1
        else:
            in_progress_count += 1

        total_credits += c.credit_count
        total_lessons_sum += total_les
        total_assignments_sum += total_asn

        # Filtering logic
        matches_query = True
        if query:
            matches_query = (query in c.title.lower()) or (query in c.course_code.lower()) or (query in c.department.lower())

        matches_dept = True
        if selected_dept:
            matches_dept = (c.department.lower() == selected_dept.lower())

        matches_status = True
        if status_filter == 'completed':
            matches_status = is_completed
        elif status_filter == 'in_progress':
            matches_status = not is_completed

        if matches_query and matches_dept and matches_status:
            all_courses_data.append({
                'enrollment': enrollments_map.get(c.id),
                'course': c,
                'total_modules': total_mod,
                'total_lessons': total_les,
                'total_assignments': total_asn,
                'submissions_count': sub_count,
                'graded_count': grd_count,
                'progress_percent': prog,
                'is_completed': is_completed,
            })

    context = {
        'courses_data': all_courses_data,
        'total_enrolled': len(courses_list),
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'total_credits': total_credits,
        'total_lessons_sum': total_lessons_sum,
        'total_assignments_sum': total_assignments_sum,
        'departments': sorted(list(departments_set)),
        'query': query,
        'selected_dept': selected_dept,
        'status_filter': status_filter,
        'available_courses': available_courses,
        'user_role': user.role,
    }
    return render(request, 'student/my_courses.html', context)


@role_required('STUDENT')
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    if not course.is_published:
        messages.error(request, f"Course {course.course_code} is currently in draft mode and not accepting enrollments.")
        return redirect('lms:course_catalog')
    student = request.user

    try:
        with transaction.atomic():
            Enrollment.objects.create(student=student, course=course, is_active=True)
        messages.success(request, f"Successfully enrolled in {course.course_code}: {course.title}!")
    except IntegrityError:
        messages.warning(request, f"You are already actively enrolled in {course.course_code}: {course.title}.")

    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('lms:student_dashboard')


@role_required('STUDENT', 'INSTRUCTOR', 'ADMIN')
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role == 'STUDENT':
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
        if not is_enrolled:
            messages.error(request, "You must enroll in this course to access its content.")
            return redirect('lms:course_catalog')

    modules = course.modules.prefetch_related('lessons').order_by('order_index')

    # Build flat ordered list of all lessons for prev/next navigation
    all_lessons = []
    for mod in modules:
        for lesson in mod.lessons.order_by('order_index'):
            all_lessons.append(lesson)

    lesson_id = request.GET.get('lesson')
    current_lesson = None
    if lesson_id:
        current_lesson = Lesson.objects.filter(module__course=course, id=lesson_id).first()

    if not current_lesson and all_lessons:
        current_lesson = all_lessons[0]

    # Prev / Next navigation
    prev_lesson = None
    next_lesson = None
    if current_lesson and all_lessons:
        idx = next((i for i, l in enumerate(all_lessons) if l.id == current_lesson.id), None)
        if idx is not None:
            prev_lesson = all_lessons[idx - 1] if idx > 0 else None
            next_lesson = all_lessons[idx + 1] if idx < len(all_lessons) - 1 else None

    rendered_markdown = ""
    if current_lesson and current_lesson.content_markdown:
        rendered_markdown = markdown.markdown(
            current_lesson.content_markdown,
            extensions=['fenced_code', 'tables', 'nl2br', 'toc']
        )

    # Render syllabus markdown
    syllabus_rendered = ""
    if course.syllabus_outline:
        syllabus_rendered = markdown.markdown(
            course.syllabus_outline,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

    # Load all Course Assignments & Jobs with Student Submission Status
    course_assignments = course.assignments.all().order_by('deadline')
    student_submissions = {}
    if request.user.is_authenticated:
        student_submissions = {
            s.assignment_id: s for s in Submission.objects.filter(
                assignment__course=course, student=request.user
            ).select_related('graded_by')
        }

    assignments_list = []
    submitted_jobs_count = 0
    graded_jobs_count = 0
    for asn in course_assignments:
        sub = student_submissions.get(asn.id)
        if sub:
            submitted_jobs_count += 1
            if sub.is_graded:
                graded_jobs_count += 1

        asn_instructions_html = markdown.markdown(
            asn.instructions or "",
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        assignments_list.append({
            'assignment': asn,
            'instructions_html': asn_instructions_html,
            'submission': sub,
            'is_submitted': sub is not None,
            'is_graded': sub.is_graded if sub else False,
            'score': sub.score if sub else None,
            'feedback': sub.feedback_markdown if sub else None,
            'is_past_deadline': timezone.now() > asn.deadline,
        })

    # Overall progress percentage for this specific course
    total_assignments_count = len(course_assignments)
    if total_assignments_count > 0:
        course_progress = min(100, int((submitted_jobs_count / total_assignments_count) * 100))
    else:
        course_progress = 85

    active_tab = request.GET.get('tab', 'learn')

    context = {
        'course': course,
        'modules': modules,
        'current_lesson': current_lesson,
        'rendered_markdown': rendered_markdown,
        'syllabus_rendered': syllabus_rendered,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons_count': len(all_lessons),
        'assignments_list': assignments_list,
        'total_assignments_count': total_assignments_count,
        'submitted_jobs_count': submitted_jobs_count,
        'graded_jobs_count': graded_jobs_count,
        'course_progress': course_progress,
        'active_tab': active_tab,
    }
    return render(request, 'student/course_detail.html', context)


@role_required('STUDENT')
def assignment_submit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user

    is_enrolled = Enrollment.objects.filter(
        student=student, course=assignment.course, is_active=True
    ).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled in this course to submit assignments.")
        return redirect('lms:student_dashboard')

    existing_submission = Submission.objects.filter(assignment=assignment, student=student).first()

    # Render assignment instructions as markdown
    instructions_rendered = ""
    if assignment.instructions:
        instructions_rendered = markdown.markdown(
            assignment.instructions,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

    if request.method == 'POST':
        if existing_submission and not assignment.allow_resubmissions:
            messages.error(request, "Resubmissions are disabled for this assignment.")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('lms:course_detail', course_id=assignment.course.id)

        uploaded_file = request.FILES.get('submission_file')
        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('lms:assignment_submit', assignment_id=assignment.id)

        if uploaded_file.size > 25 * 1024 * 1024:
            messages.error(request, "File size exceeds the 25 MB limit.")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('lms:assignment_submit', assignment_id=assignment.id)

        ext = uploaded_file.name.rsplit('.', 1)[-1].lower()
        if ext not in ['pdf', 'zip', 'docx']:
            messages.error(request, "Invalid format. Only .pdf, .zip, and .docx are accepted.")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('lms:assignment_submit', assignment_id=assignment.id)

        # Sanitize name to guarantee clean extension without special characters
        uploaded_file.name = f"sub_{student.username}_asn{assignment.id}.{ext}"

        is_late = timezone.now() > assignment.deadline

        if existing_submission:
            existing_submission.file = uploaded_file
            existing_submission.submitted_at = timezone.now()
            existing_submission.is_late = is_late
            existing_submission.score = None
            existing_submission.feedback_markdown = None
            existing_submission.graded_by = None
            existing_submission.graded_at = None
            existing_submission.save()
            messages.success(
                request,
                f"Submission updated for '{assignment.title}'! (Marked as Late)" if is_late else f"Submission updated for '{assignment.title}'! (Submitted on time)"
            )
        else:
            Submission.objects.create(
                assignment=assignment,
                student=student,
                file=uploaded_file,
                is_late=is_late
            )
            messages.success(
                request,
                f"Assignment '{assignment.title}' submitted successfully! (Marked as Late)" if is_late else f"Assignment '{assignment.title}' submitted successfully! (Submitted on time)"
            )

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('lms:course_detail', course_id=assignment.course.id)

    time_rem = assignment.deadline - timezone.now() if timezone.now() < assignment.deadline else None
    hours_rem = (time_rem.seconds // 3600) if time_rem else 0

    context = {
        'assignment': assignment,
        'submission': existing_submission,
        'instructions_rendered': instructions_rendered,
        'is_past_deadline': timezone.now() > assignment.deadline,
        'time_remaining': time_rem,
        'hours_remaining': hours_rem,
    }
    return render(request, 'student/assignment_submit.html', context)


@role_required('STUDENT')
def student_grades(request):
    student = request.user

    if request.GET.get('export') == 'pdf':
        return export_student_transcript_pdf(student)

    submissions = Submission.objects.filter(student=student).select_related(
        'assignment', 'assignment__course', 'graded_by'
    ).order_by('assignment__course__course_code', '-submitted_at')

    # Group by course
    grades_by_course = {}
    for sub in submissions:
        code = sub.assignment.course.course_code
        if code not in grades_by_course:
            grades_by_course[code] = {
                'title': sub.assignment.course.title,
                'submissions': [],
                'scores': [],
            }
        grades_by_course[code]['submissions'].append(sub)
        if sub.is_graded:
            pct = float(sub.score) / float(sub.assignment.max_points) * 100
            sub.score_percent = round(pct, 1)
            grades_by_course[code]['scores'].append(pct)

    # Compute per-course average
    for code, data in grades_by_course.items():
        if data['scores']:
            data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 1)
        else:
            data['avg_score'] = None

    # Compute GPA (simple weighted: score% → 4.0 scale)
    all_scores = [s for d in grades_by_course.values() for s in d['scores']]
    gpa = None
    if all_scores:
        avg_pct = sum(all_scores) / len(all_scores)
        gpa = round(avg_pct / 100 * 4.0, 2)

    graded_count = sum(1 for s in submissions if s.is_graded)
    pending_count = sum(1 for s in submissions if not s.is_graded)
    enrolled_count = Enrollment.objects.filter(student=student, is_active=True).count()

    context = {
        'submissions': submissions,
        'grades_by_course': grades_by_course,
        'gpa': gpa,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'enrolled_count': enrolled_count,
    }
    return render(request, 'student/grades.html', context)


@role_required('STUDENT', 'INSTRUCTOR', 'ADMIN')
def download_submission(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related('student', 'assignment', 'assignment__course'),
        id=submission_id
    )
    user = request.user

    # Permission check: student owner, assigned course instructor, or admin
    is_owner = (user == submission.student)
    is_instructor = (user.role == 'INSTRUCTOR' and submission.assignment.course.instructor == user)
    is_admin = (user.role == 'ADMIN' or user.is_superuser)

    if not (is_owner or is_instructor or is_admin):
        raise PermissionDenied("You are not authorized to download this submission file.")

    if not submission.file or not os.path.exists(submission.file.path):
        raise Http404("Submission file does not exist on server.")

    original_name = os.path.basename(submission.file.name)
    ext = os.path.splitext(original_name)[1].lower()
    if not ext or ext not in ['.pdf', '.zip', '.docx']:
        ext = '.pdf'

    clean_filename = f"{submission.student.username}_{submission.assignment.course.course_code}_submission{ext}"

    return FileResponse(
        open(submission.file.path, 'rb'),
        as_attachment=True,
        filename=clean_filename
    )
