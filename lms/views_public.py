from django.shortcuts import render
from django.db.models import Count
from .models import Course, Enrollment


TESTIMONIALS = [
    {
        'name': 'John Doe', 'initials': 'JD', 'course': 'CS-101 Student',
        'quote': "The structured modules with syntax-highlighted code examples made complex algorithms click for me. Prof. Smith's feedback is incredibly detailed."
    },
    {
        'name': 'Priya Sharma', 'initials': 'PS', 'course': 'SEC-401 Student',
        'quote': 'The CTF challenges are genuinely hard and genuinely fun. I landed a security internship partly because of skills I built in this course.'
    },
    {
        'name': 'Alice Wu', 'initials': 'AW', 'course': 'UX-301 Student',
        'quote': "Dr. Chen's design crits are intense but fair. My portfolio is miles better than it was at the start of the semester."
    },
    {
        'name': 'Mike Ross', 'initials': 'MR', 'course': 'DS-201 Student',
        'quote': "The EDA notebooks taught me how to actually think about data before jumping to a model. Best data science course I've taken."
    },
    {
        'name': 'Emma Jones', 'initials': 'EJ', 'course': 'CS-101 Student',
        'quote': 'The PDF transcript is a nice touch — I attached it to my internship application and it impressed the interviewer.'
    },
    {
        'name': 'Carlos Perez', 'initials': 'CP', 'course': 'DS-201 Student',
        'quote': 'The gradebook is transparent and the qualitative feedback is what sets UnivLMS apart from platforms that just give you a number.'
    },
]


from accounts.models import User


def index(request):
    featured_courses = Course.objects.filter(is_active=True, is_published=True).select_related('instructor').annotate(
        student_count=Count('enrollments')
    )[:6]

    mentors_list = User.objects.filter(role=User.Role.INSTRUCTOR, is_active=True).prefetch_related('instructed_courses')[:4]
    total_courses = Course.objects.filter(is_active=True, is_published=True).count()
    total_enrollments = Enrollment.objects.filter(is_active=True).count()

    context = {
        'featured_courses': featured_courses,
        'mentors': mentors_list,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'testimonials': TESTIMONIALS,
    }
    return render(request, 'public/index.html', context)


def mentors(request):
    query = request.GET.get('q', '').strip()
    dept = request.GET.get('dept', '').strip()

    mentors_qs = User.objects.filter(role=User.Role.INSTRUCTOR, is_active=True).prefetch_related('instructed_courses')

    if query:
        mentors_qs = (
            mentors_qs.filter(first_name__icontains=query) |
            mentors_qs.filter(last_name__icontains=query) |
            mentors_qs.filter(username__icontains=query)
        )

    mentors_data = []
    for mentor in mentors_qs:
        courses = mentor.instructed_courses.filter(is_active=True, is_published=True)
        if dept and dept.lower() not in mentor.mentor_department.lower():
            continue
        total_students = sum(c.total_students for c in courses)
        mentors_data.append({
            'user': mentor,
            'courses': courses,
            'courses_count': courses.count(),
            'total_students': total_students,
        })

    departments = [
        'Computer Science Department',
        'Design & Interactive Media',
        'Information Security & Cloud',
    ]

    total_mentors = len(mentors_data)
    total_courses_taught = sum(m['courses_count'] for m in mentors_data)

    context = {
        'mentors': mentors_data,
        'departments': departments,
        'selected_dept': dept,
        'query': query,
        'total_mentors': total_mentors,
        'total_courses_taught': total_courses_taught,
    }
    return render(request, 'public/mentors.html', context)


def course_catalog(request):
    query = request.GET.get('q', '').strip()
    dept = request.GET.get('dept', '').strip()

    courses = Course.objects.filter(is_active=True, is_published=True).select_related('instructor')

    if query:
        courses = (
            courses.filter(title__icontains=query) |
            courses.filter(course_code__icontains=query) |
            courses.filter(department__icontains=query)
        )

    if dept:
        courses = courses.filter(department__iexact=dept)

    departments = Course.objects.filter(is_active=True, is_published=True).values_list('department', flat=True).distinct()

    enrolled_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'is_student') and request.user.is_student:
        enrolled_ids = list(
            request.user.enrollments.filter(is_active=True).values_list('course_id', flat=True)
        )

    context = {
        'courses': courses,
        'departments': departments,
        'query': query,
        'selected_dept': dept,
        'enrolled_ids': enrolled_ids,
    }
    return render(request, 'public/catalog.html', context)


def course_detail(request, course_id):
    from django.shortcuts import get_object_or_404
    import markdown

    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related('modules__lessons', 'assignments'),
        id=course_id,
        is_active=True
    )

    is_enrolled = False
    if request.user.is_authenticated and hasattr(request.user, 'is_student') and request.user.is_student:
        is_enrolled = course.enrollments.filter(student=request.user, is_active=True).exists()

    syllabus_html = ''
    if course.syllabus_outline:
        syllabus_html = markdown.markdown(
            course.syllabus_outline,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

    modules = course.modules.all().order_by('order_index')
    assignments = course.assignments.all().order_by('deadline')

    context = {
        'course': course,
        'syllabus_html': syllabus_html,
        'modules': modules,
        'assignments': assignments,
        'is_enrolled': is_enrolled,
        'total_lessons': sum(m.lessons.count() for m in modules),
        'total_students': course.total_students,
    }
    return render(request, 'public/course_detail.html', context)
