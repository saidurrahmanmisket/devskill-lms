from django.urls import path
from . import views_public, views_student, views_faculty, views_admin

app_name = 'lms'

urlpatterns = [
    # Public & Catalog
    path('', views_public.index, name='index'),
    path('courses/', views_public.course_catalog, name='course_catalog'),
    path('courses/<int:course_id>/details/', views_public.course_detail, name='public_course_detail'),
    path('mentors/', views_public.mentors, name='mentors'),

    # Student Workspace
    path('student/dashboard/', views_student.student_dashboard, name='student_dashboard'),
    path('student/my-courses/', views_student.student_my_courses, name='student_my_courses'),
    path('courses/<int:course_id>/enroll/', views_student.enroll_course, name='enroll_course'),
    path('student/courses/<int:course_id>/', views_student.course_detail, name='course_detail'),
    path('student/assignments/<int:assignment_id>/submit/', views_student.assignment_submit, name='assignment_submit'),
    path('student/grades/', views_student.student_grades, name='student_grades'),
    path('submissions/<int:submission_id>/download/', views_student.download_submission, name='download_submission'),

    # Faculty Workspace
    path('faculty/dashboard/', views_faculty.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/my-courses/', views_faculty.faculty_my_courses, name='faculty_my_courses'),
    path('faculty/courses/create/', views_faculty.course_create, name='course_create'),
    path('faculty/courses/<int:course_id>/curriculum/', views_faculty.curriculum_builder, name='curriculum_builder'),
    path('faculty/courses/<int:course_id>/toggle-publish/', views_faculty.course_toggle_publish, name='course_toggle_publish'),
    path('faculty/courses/<int:course_id>/delete/', views_faculty.course_delete, name='course_delete'),
    path('faculty/courses/<int:course_id>/assignments/dispatch/', views_faculty.assignment_dispatch, name='assignment_dispatch'),
    path('faculty/gradebook/', views_faculty.faculty_gradebook, name='faculty_gradebook'),
    path('faculty/submissions/<int:submission_id>/grade/', views_faculty.grade_submission, name='grade_submission'),
    # AJAX curriculum endpoints
    path('faculty/courses/<int:course_id>/modules/add/', views_faculty.ajax_add_module, name='ajax_add_module'),
    path('faculty/modules/<int:module_id>/delete/', views_faculty.ajax_delete_module, name='ajax_delete_module'),
    path('faculty/modules/<int:module_id>/lessons/add/', views_faculty.ajax_add_lesson, name='ajax_add_lesson'),
    path('faculty/lessons/<int:lesson_id>/delete/', views_faculty.ajax_delete_lesson, name='ajax_delete_lesson'),

    # Administrative Governance & Audit Trail
    path('admin-portal/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/users/', views_admin.admin_users, name='admin_users'),
    path('admin-portal/users/<int:user_id>/toggle-active/', views_admin.admin_toggle_user_active, name='admin_toggle_user_active'),
    path('admin-portal/users/import-csv/', views_admin.admin_import_csv, name='admin_import_csv'),
    path('admin-portal/audit-logs/', views_admin.admin_audit_logs, name='admin_audit_logs'),
    path('admin-portal/courses/<int:course_id>/delete/', views_admin.admin_delete_course, name='admin_delete_course'),
]
