from django.contrib import admin
from .models import Course, Module, Lesson, Assignment, Submission, AuditLog, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'department', 'instructor', 'credit_count', 'is_active', 'created_at')
    list_filter = ('department', 'is_active')
    search_fields = ('course_code', 'title', 'instructor__username', 'instructor__first_name', 'instructor__last_name')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order_index')
    list_filter = ('course',)
    search_fields = ('title', 'course__course_code')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order_index')
    list_filter = ('module__course',)
    search_fields = ('title',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'max_points', 'deadline', 'allow_resubmissions')
    list_filter = ('course',)
    search_fields = ('title', 'course__course_code')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'score', 'is_late', 'submitted_at')
    list_filter = ('is_late', 'assignment__course')
    search_fields = ('student__username', 'student__academic_id', 'assignment__title')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'actor', 'target_entity', 'timestamp')
    list_filter = ('action_type',)
    search_fields = ('actor__username', 'target_entity')
    readonly_fields = ('action_type', 'actor', 'target_entity', 'timestamp')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('student__username', 'course__course_code')
