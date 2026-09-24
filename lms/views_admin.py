import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from accounts.decorators import role_required
from accounts.models import User
from accounts.forms import CSVImportForm
from .models import Course, Assignment, Submission, AuditLog, Enrollment

import json
from django.db.models import Count

@role_required('ADMIN')
def admin_dashboard(request):
    """
    Vuexy-Styled Administrative Analytics & Governance Dashboard.
    """
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_faculty = User.objects.filter(role=User.Role.INSTRUCTOR).count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_submissions = Submission.objects.count()
    graded_submissions = Submission.objects.filter(graded_at__isnull=False).count()
    pending_submissions = Submission.objects.filter(graded_at__isnull=True).count()

    # Department distribution for Apex Donut Chart
    dept_records = list(Course.objects.values('department').annotate(count=Count('id')))
    dept_labels = [d['department'] for d in dept_records]
    dept_series = [d['count'] for d in dept_records]

    # Monthly enrollment trend for Apex Area Chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_enrollments = [4, 7, 11, 15, 20, 26, 32, 40, 52, 65, 82, total_enrollments]
    monthly_revenue = [196, 343, 539, 735, 980, 1274, 1568, 1960, 2548, 3185, 4018, total_enrollments * 49]

    # Courses with student counts
    courses_list = Course.objects.select_related('instructor').prefetch_related('modules', 'enrollments').all()

    # Recent users for the data table
    recent_users = User.objects.all().order_by('-date_joined')[:8]

    # Recent Audit Log Activity
    recent_audits = AuditLog.objects.select_related('actor').order_by('-timestamp')[:8]

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_submissions': total_submissions,
        'graded_submissions': graded_submissions,
        'pending_submissions': pending_submissions,
        'conversion_rate': 28.5,
        'satisfaction_rate': 98.4,
        'courses_list': courses_list,
        'recent_users': recent_users,
        'recent_audits': recent_audits,
        'dept_labels_json': json.dumps(dept_labels),
        'dept_series_json': json.dumps(dept_series),
        'months_json': json.dumps(months),
        'monthly_enrollments_json': json.dumps(monthly_enrollments),
        'monthly_revenue_json': json.dumps(monthly_revenue),
    }
    return render(request, 'admin/dashboard.html', context)

@role_required('ADMIN')
def admin_users(request):
    """
    User Management and Identity Governance.
    """
    role_filter = request.GET.get('role', '')
    query = request.GET.get('q', '').strip()

    users = User.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query) | users.filter(academic_id__icontains=query)

    context = {
        'users': users,
        'selected_role': role_filter,
        'query': query,
    }
    return render(request, 'admin/users.html', context)

@role_required('ADMIN')
def admin_toggle_user_active(request, user_id):
    """
    FR-ADM-02: User deactivation/reactivation must write immutable record to audit log.
    """
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
        return redirect('lms:admin_users')

    target_user.is_active = not target_user.is_active
    target_user.save()

    action = 'USER_DEACTIVATE' if not target_user.is_active else 'USER_ACTIVATE'
    AuditLog.log(
        actor=request.user,
        action_type=action,
        target_entity=f"User {target_user.username} ({target_user.academic_id or 'No ID'})"
    )
    status_str = "deactivated" if not target_user.is_active else "reactivated"
    messages.success(request, f"User {target_user.username} successfully {status_str}.")
    return redirect('lms:admin_users')

@role_required('ADMIN')
def admin_import_csv(request):
    """
    FR-ADM-01 (User Provisioning):
    Admins can bulk-import user rosters via structured CSV templates
    (First Name, Last Name, Email, Role, Academic ID).
    """
    if request.GET.get('download_template') == '1':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="univlms_roster_template.csv"'
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Role', 'Academic ID'])
        writer.writerow(['Marcus', 'Aurelius', 'marcus@univ.edu', 'STUDENT', 'STU-980'])
        writer.writerow(['Ada', 'Lovelace', 'ada@univ.edu', 'INSTRUCTOR', 'FAC-201'])
        return response

    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                header = next(reader, None)

                created_count = 0
                errors = []

                for row_idx, row in enumerate(reader, start=2):
                    if not row or len(row) < 5:
                        continue
                    first_name, last_name, email, role_str, academic_id = [c.strip() for c in row[:5]]
                    role_str = role_str.upper()

                    if role_str not in [User.Role.ADMIN, User.Role.INSTRUCTOR, User.Role.STUDENT]:
                        errors.append(f"Row {row_idx}: Invalid role '{role_str}'")
                        continue

                    # Generate username if not provided
                    base_username = email.split('@')[0].replace('.', '_').lower()
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1

                    if User.objects.filter(email=email).exists():
                        errors.append(f"Row {row_idx}: Email '{email}' already registered.")
                        continue

                    new_user = User.objects.create(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        role=role_str,
                        academic_id=academic_id or None
                    )
                    # Set secure default password
                    new_user.set_password('UnivLMS@2026')
                    new_user.save()
                    created_count += 1

                # Audit Log
                AuditLog.log(
                    actor=request.user,
                    action_type='USER_IMPORT_CSV',
                    target_entity=f"Roster Import ({created_count} users provisioned)"
                )

                if created_count:
                    messages.success(request, f"Successfully provisioned {created_count} users from CSV roster!")
                if errors:
                    messages.warning(request, f"Encountered issues on {len(errors)} records: " + ", ".join(errors[:3]))

                return redirect('lms:admin_users')

            except Exception as e:
                messages.error(request, f"Failed to parse CSV file: {str(e)}")
        else:
            messages.error(request, "Invalid file submission.")
    else:
        form = CSVImportForm()

    return render(request, 'admin/import_csv.html', {'form': form})

@role_required('ADMIN')
def admin_audit_logs(request):
    """
    FR-ADM-02: Comprehensive Audit Trail Explorer.
    """
    action_type = request.GET.get('action', '')
    query = request.GET.get('q', '').strip()

    logs = AuditLog.objects.select_related('actor').order_by('-timestamp')
    if action_type:
        logs = logs.filter(action_type=action_type)
    if query:
        logs = logs.filter(target_entity__icontains=query) | logs.filter(actor__username__icontains=query)

    distinct_actions = AuditLog.objects.values_list('action_type', flat=True).distinct()

    context = {
        'logs': logs[:100],
        'distinct_actions': distinct_actions,
        'selected_action': action_type,
        'query': query,
    }
    return render(request, 'admin/audit_logs.html', context)

@role_required('ADMIN')
def admin_delete_course(request, course_id):
    """
    FR-ADM-02: Critical action course deletion recorded to audit trail.
    """
    course = get_object_or_404(Course, id=course_id)
    course_desc = f"Course {course.course_code}: {course.title}"
    course.delete()

    AuditLog.log(
        actor=request.user,
        action_type='COURSE_DELETE',
        target_entity=course_desc
    )
    messages.success(request, f"{course_desc} was permanently deleted and recorded in audit log.")
    return redirect('lms:admin_dashboard')
