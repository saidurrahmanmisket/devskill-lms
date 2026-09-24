import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def validate_lesson_media(file):
    """
    FR-CRS-03: Attachments uploaded by instructors must be validated
    on MIME type and capped at 50 MB per file.
    """
    max_size_mb = 50
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(_(f"File size exceeds maximum limit of {max_size_mb} MB."))

    # Allowed extensions
    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm', '.mp3', '.wav', '.ogg', '.zip', '.docx', '.pptx', '.txt', '.md']
    if ext not in allowed_exts:
        raise ValidationError(_(f"Unsupported file format '{ext}'. Allowed: {', '.join(allowed_exts)}"))

def validate_submission_file(file):
    """
    FR-ASN-02: Support document uploads (.pdf, .zip, .docx) up to 25 MB.
    """
    max_size_mb = 25
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(_(f"Submission file exceeds maximum size of {max_size_mb} MB."))

    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = ['.pdf', '.zip', '.docx']
    if ext not in allowed_exts:
        raise ValidationError(_(f"Unsupported file format '{ext}'. Only .pdf, .zip, and .docx are permitted."))

class Course(models.Model):
    course_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, help_text=_("Short public course description shown in the catalog."))
    department = models.CharField(max_length=150)
    credit_count = models.PositiveIntegerField(default=3)
    syllabus_outline = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        blank=True,
        null=True,
        help_text=_("Course cover image shown in the catalog. Recommended: 16:9 ratio.")
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructed_courses'
    )
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(
        default=True,
        help_text=_("Designates whether this course is published to the public catalog.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['course_code']

    def __str__(self):
        return f"{self.course_code}: {self.title}"

    @property
    def total_students(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def total_modules(self):
        return self.modules.count()

    @property
    def total_assignments(self):
        return self.assignments.count()

    @property
    def image_url(self):
        mapping = {
            'CS-101': 'images/courses/course_cs101.jpg',
            'DS-201': 'images/courses/course_ds201.jpg',
            'UX-301': 'images/courses/course_ux301.jpg',
            'SEC-401': 'images/courses/course_sec401.jpg',
            'CLD-501': 'images/courses/course_cld501.jpg',
            'AI-601': 'images/courses/course_ai601.jpg',
        }
        return mapping.get(self.course_code, 'images/courses/course_cs101.jpg')

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'enrollments'
        constraints = [
            models.UniqueConstraint(fields=['student', 'course'], name='unique_student_course_enrollment')
        ]
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} -> {self.course.course_code}"

class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=255)
    order_index = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'modules'
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.course.course_code} - Module {self.order_index}: {self.title}"

class Lesson(models.Model):
    class LessonType(models.TextChoices):
        TEXT = 'TEXT', _('Text / Markdown')
        VIDEO = 'VIDEO', _('Video')
        AUDIO = 'AUDIO', _('Audio')
        PDF = 'PDF', _('PDF Document')
        IMAGE = 'IMAGE', _('Image')
        LINK = 'LINK', _('External Link')

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(
        max_length=10,
        choices=LessonType.choices,
        default=LessonType.TEXT,
        help_text=_("Type of lesson content")
    )
    content_markdown = models.TextField(blank=True, null=True, help_text=_("Rich text/markdown content for TEXT type lessons."))
    external_url = models.URLField(blank=True, null=True, help_text=_("External URL for LINK type lessons."))
    duration_minutes = models.PositiveIntegerField(default=0, help_text=_("Estimated duration in minutes."))
    media_file = models.FileField(
        upload_to='lessons/media/',
        validators=[validate_lesson_media],
        blank=True,
        null=True,
        help_text=_("Upload: video (.mp4/.webm), audio (.mp3/.wav), PDF, or image. Max 50 MB.")
    )
    order_index = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lessons'
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.module.title} - Lesson {self.order_index}: {self.title}"

class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)
    release_at = models.DateTimeField()
    deadline = models.DateTimeField()
    max_points = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    allow_resubmissions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['-deadline']

    def __str__(self):
        return f"{self.course.course_code}: {self.title} (Max: {self.max_points})"

    @property
    def is_past_deadline(self):
        return timezone.now() > self.deadline

    @property
    def is_released(self):
        return timezone.now() >= self.release_at

class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    file = models.FileField(
        upload_to='submissions/',
        validators=[validate_submission_file],
        help_text=_("Allowed: .pdf, .zip, .docx up to 25 MB")
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback_markdown = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'submissions'
        constraints = [
            models.UniqueConstraint(fields=['assignment', 'student'], name='unique_assignment_student_submission')
        ]
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"

    @property
    def is_graded(self):
        return self.score is not None

class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action_type = models.CharField(
        max_length=100,
        help_text=_("e.g., USER_DEACTIVATE, GRADE_OVERRIDE, COURSE_DELETE, USER_IMPORT_CSV")
    )
    target_entity = models.CharField(
        max_length=255,
        help_text=_("Entity name and identifier affected")
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.actor.username} -> {self.action_type} on {self.target_entity}"

    @classmethod
    def log(cls, actor, action_type, target_entity):
        return cls.objects.create(
            actor=actor,
            action_type=action_type,
            target_entity=target_entity
        )
