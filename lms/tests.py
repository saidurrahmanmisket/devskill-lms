import io
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from lms.models import Course, Module, Lesson, Enrollment, Assignment, Submission, AuditLog

class UnivLMSVerificationTests(TestCase):
    """
    Verification & Quality Acceptance Criteria Test Suite (SRS Section 6).
    """

    def setUp(self):
        self.client = Client()

        # Users
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.edu',
            password='Password@123',
            role=User.Role.ADMIN,
            academic_id='ADM-TEST'
        )
        self.instructor = User.objects.create_user(
            username='instructor_test',
            email='instructor@test.edu',
            password='Password@123',
            role=User.Role.INSTRUCTOR,
            academic_id='FAC-TEST'
        )
        self.student = User.objects.create_user(
            username='student_test',
            email='student@test.edu',
            password='Password@123',
            role=User.Role.STUDENT,
            academic_id='STU-TEST'
        )

        # Course
        self.course = Course.objects.create(
            course_code='CS-TEST',
            title='Test Computer Science',
            department='Computer Science',
            credit_count=3,
            instructor=self.instructor
        )

        # Module & Lesson
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1',
            order_index=1
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1',
            content_markdown='# Heading\nTest content',
            order_index=1
        )

        # Active Assignment
        self.assignment_future = Assignment.objects.create(
            course=self.course,
            title='Future Assignment',
            instructions='Test instructions',
            release_at=timezone.now() - timedelta(days=1),
            deadline=timezone.now() + timedelta(days=5),
            max_points=Decimal('100.00'),
            allow_resubmissions=True
        )

        # Past Deadline Assignment
        self.assignment_past = Assignment.objects.create(
            course=self.course,
            title='Past Assignment',
            instructions='Test past instructions',
            release_at=timezone.now() - timedelta(days=10),
            deadline=timezone.now() - timedelta(days=2),
            max_points=Decimal('100.00'),
            allow_resubmissions=True
        )

    def test_criterion_1_unauthenticated_access_redirects(self):
        """
        SRS Criterion 1:
        Non-authenticated access to /faculty/gradebook/ results in HTTP 302 Redirect to /login/?next=...
        """
        gradebook_url = reverse('lms:faculty_gradebook')
        response = self.client.get(gradebook_url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('accounts:login')
        self.assertTrue(response.url.startswith(login_url))
        self.assertIn(f"next={gradebook_url}", response.url)

    def test_criterion_2_role_based_access_forbidden_for_student(self):
        """
        Student attempting to access faculty gradebook receives 403 Forbidden.
        """
        self.client.login(username='student_test', password='Password@123')
        gradebook_url = reverse('lms:faculty_gradebook')
        response = self.client.get(gradebook_url)
        self.assertEqual(response.status_code, 403)

    def test_criterion_3_double_enrollment_clean_error(self):
        """
        SRS Criterion 2:
        Student double-enrolls in same course instance results in a captured
        IntegrityError and a clean user-facing error message.
        """
        self.client.login(username='student_test', password='Password@123')
        enroll_url = reverse('lms:enroll_course', kwargs={'course_id': self.course.id})

        # First enrollment
        resp1 = self.client.get(enroll_url, follow=True)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)

        # Second enrollment (attempt double enroll)
        resp2 = self.client.get(enroll_url, follow=True)
        self.assertEqual(resp2.status_code, 200)
        # Verify enrollment count remains 1 (no duplicate created, no crash)
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)
        # Verify clean warning message in messages
        messages = list(resp2.context['messages'])
        self.assertTrue(any("already actively enrolled" in str(m) for m in messages))

    def test_criterion_4_late_submission_flag(self):
        """
        SRS Criterion 3:
        Submission uploaded after the deadline timestamp results in the database
        record being marked as is_late=True.
        """
        # Enroll student
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        self.client.login(username='student_test', password='Password@123')

        # 1. On-time submission
        file_on_time = SimpleUploadedFile("solution_ontime.pdf", b"%PDF-1.4 file content", content_type="application/pdf")
        submit_url_ontime = reverse('lms:assignment_submit', kwargs={'assignment_id': self.assignment_future.id})
        resp_ontime = self.client.post(submit_url_ontime, {'submission_file': file_on_time}, follow=True)
        self.assertEqual(resp_ontime.status_code, 200)

        sub_ontime = Submission.objects.get(assignment=self.assignment_future, student=self.student)
        self.assertFalse(sub_ontime.is_late)

        # 2. Late submission
        file_late = SimpleUploadedFile("solution_late.docx", b"PK docx content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        submit_url_late = reverse('lms:assignment_submit', kwargs={'assignment_id': self.assignment_past.id})
        resp_late = self.client.post(submit_url_late, {'submission_file': file_late}, follow=True)
        self.assertEqual(resp_late.status_code, 200)

        sub_late = Submission.objects.get(assignment=self.assignment_past, student=self.student)
        self.assertTrue(sub_late.is_late)

    def test_grade_override_creates_audit_log(self):
        """
        FR-ADM-02: Grade overrides write immutable records to the audit log.
        """
        # Setup submission
        file_sub = SimpleUploadedFile("solution.pdf", b"%PDF-1.4", content_type="application/pdf")
        sub = Submission.objects.create(
            assignment=self.assignment_future,
            student=self.student,
            file=file_sub,
            score=Decimal('85.00')
        )

        self.client.login(username='instructor_test', password='Password@123')
        grade_url = reverse('lms:grade_submission', kwargs={'submission_id': sub.id})

        # Override grade to 95.00
        resp = self.client.post(grade_url, {
            'score': '95.00',
            'feedback_markdown': 'Revised after regrade request.'
        }, follow=True)

        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.score, Decimal('95.00'))

        # Verify audit log created
        audit_entry = AuditLog.objects.filter(action_type='GRADE_OVERRIDE').first()
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.actor, self.instructor)
        self.assertIn("85.00 -> 95.00", audit_entry.target_entity)

    def test_export_grades_csv_and_pdf(self):
        """
        FR-ADM-03: Export student grade-sheets to CSV and PDF formats.
        """
        self.client.login(username='instructor_test', password='Password@123')
        gradebook_url = reverse('lms:faculty_gradebook')

        # CSV Export
        resp_csv = self.client.get(f"{gradebook_url}?course_id={self.course.id}&export=csv")
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename=', resp_csv['Content-Disposition'])

        # PDF Export
        resp_pdf = self.client.get(f"{gradebook_url}?course_id={self.course.id}&export=pdf")
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf['Content-Type'], 'application/pdf')
        # Check PDF header signature
        self.assertTrue(resp_pdf.content.startswith(b'%PDF'))

    def test_admin_user_deactivation_creates_audit_log(self):
        """
        FR-ADM-02: User deactivation writes immutable record to audit log.
        """
        self.client.login(username='admin_test', password='Password@123')
        toggle_url = reverse('lms:admin_toggle_user_active', kwargs={'user_id': self.student.id})
        resp = self.client.get(toggle_url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)

        audit = AuditLog.objects.filter(action_type='USER_DEACTIVATE').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.actor, self.admin)
        self.assertIn(self.student.username, audit.target_entity)

    def test_admin_bulk_csv_import(self):
        """
        FR-ADM-01: Bulk-import user rosters via structured CSV templates.
        """
        self.client.login(username='admin_test', password='Password@123')
        import_url = reverse('lms:admin_import_csv')

        csv_content = (
            "First Name,Last Name,Email,Role,Academic ID\n"
            "Grace,Hopper,hopper@univ.edu,INSTRUCTOR,FAC-303\n"
            "Claude,Shannon,shannon@univ.edu,STUDENT,STU-777\n"
        ).encode('utf-8')

        csv_file = SimpleUploadedFile("roster.csv", csv_content, content_type="text/csv")
        resp = self.client.post(import_url, {'csv_file': csv_file}, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Verify users created
        hopper = User.objects.filter(email='hopper@univ.edu').first()
        self.assertIsNotNone(hopper)
        self.assertEqual(hopper.role, User.Role.INSTRUCTOR)
        self.assertEqual(hopper.academic_id, 'FAC-303')

        shannon = User.objects.filter(email='shannon@univ.edu').first()
        self.assertIsNotNone(shannon)
        self.assertEqual(shannon.role, User.Role.STUDENT)
        self.assertEqual(shannon.academic_id, 'STU-777')
