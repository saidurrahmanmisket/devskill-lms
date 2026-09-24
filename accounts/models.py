from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        INSTRUCTOR = 'INSTRUCTOR', _('Instructor')
        STUDENT = 'STUDENT', _('Student')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User access level and workspace permission')
    )
    academic_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Institutional ID from roster (e.g. ADM-001, FAC-101, STU-901)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def get_full_name_or_username(self):
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.username

    @property
    def mentor_avatar_url(self):
        mapping = {
            'prof_smith': 'images/mentors/mentor_alan_smith.jpg',
            'dr_chen': 'images/mentors/mentor_elena_chen.jpg',
            'prof_morgan': 'images/mentors/mentor_james_morgan.jpg',
        }
        return mapping.get(self.username, 'images/mentors/mentor_alan_smith.jpg')

    @property
    def mentor_title(self):
        mapping = {
            'prof_smith': 'Lead Professor of Computer Science & Software Engineering',
            'dr_chen': 'Director of Human-Computer Interaction & UI/UX Design',
            'prof_morgan': 'Chair of Cybersecurity Systems & Distributed Cloud Defense',
        }
        return mapping.get(self.username, 'Senior Faculty Mentor')

    @property
    def mentor_bio(self):
        mapping = {
            'prof_smith': 'Former Senior Tech Lead at Google & MIT Fellow with 14+ years designing high-throughput distributed systems and full-stack software architectures.',
            'dr_chen': 'Award-winning Design Director and Stanford alumni specializing in cognitive ergonomics, design tokens, and user experience systems.',
            'prof_morgan': 'Certified Ethical Hacker, enterprise security consultant, and researcher focusing on threat defense, zero-trust infrastructure, and applied cryptography.',
        }
        return mapping.get(self.username, 'Dedicated educator committed to student excellence and practical technical mastery.')

    @property
    def mentor_rating(self):
        mapping = {
            'prof_smith': '4.96',
            'dr_chen': '4.98',
            'prof_morgan': '4.93',
        }
        return mapping.get(self.username, '4.90')

    @property
    def mentor_department(self):
        mapping = {
            'prof_smith': 'Computer Science Department',
            'dr_chen': 'Design & Interactive Media',
            'prof_morgan': 'Information Security & Cloud',
        }
        return mapping.get(self.username, 'Engineering & Technology')

    @property
    def mentor_specialties(self):
        mapping = {
            'prof_smith': ['Python Engineering', 'Algorithms', 'Distributed Systems', 'Data Science'],
            'dr_chen': ['UI/UX Design', 'Figma Systems', 'Product Design', 'User Research'],
            'prof_morgan': ['Network Defense', 'Penetration Testing', 'Cloud Security', 'DevOps'],
        }
        return mapping.get(self.username, ['Software Engineering', 'Technical Architecture'])

    def __str__(self):
        return f"{self.get_full_name_or_username()} ({self.role})"
