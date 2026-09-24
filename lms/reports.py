import csv
import io
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .models import Submission, Course, Enrollment

def export_course_grades_csv(course):
    """
    FR-ADM-03: Export student grade-sheet metrics to CSV format.
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="UnivLMS_{course.course_code}_Grades_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Course Code', 'Course Title', 'Student Academic ID',
        'Student Full Name', 'Student Email', 'Assignment Title',
        'Score', 'Max Points', 'Percentage', 'Submission Status',
        'Submission Timestamp', 'Graded By'
    ])

    submissions = Submission.objects.filter(assignment__course=course).select_related(
        'student', 'assignment', 'graded_by'
    ).order_by('student__last_name', 'assignment__title')

    for sub in submissions:
        pct = f"{(sub.score / sub.assignment.max_points * 100):.1f}%" if sub.score is not None and sub.assignment.max_points else "N/A"
        late_status = "LATE" if sub.is_late else "ON-TIME"
        graded_by = sub.graded_by.get_full_name_or_username() if sub.graded_by else "Ungraded"

        writer.writerow([
            course.course_code,
            course.title,
            sub.student.academic_id or 'N/A',
            sub.student.get_full_name_or_username(),
            sub.student.email,
            sub.assignment.title,
            sub.score if sub.score is not None else "Pending",
            sub.assignment.max_points,
            pct,
            late_status,
            sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            graded_by
        ])

    return response

def export_course_grades_pdf(course):
    """
    FR-ADM-03: Dynamic institutional PDF generation via ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0A291F')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#576860'),
        leading=14
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11
    )

    story = []

    # Header / Title
    story.append(Paragraph("UnivLMS Institutional Academic Report", title_style))
    story.append(Paragraph(
        f"<b>Course:</b> {course.course_code} - {course.title} &nbsp;|&nbsp; "
        f"<b>Department:</b> {course.department} &nbsp;|&nbsp; "
        f"<b>Instructor:</b> {course.instructor.get_full_name_or_username()}",
        subtitle_style
    ))
    story.append(Paragraph(
        f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M UTC')} &nbsp;|&nbsp; "
        f"Credits: {course.credit_count} &nbsp;|&nbsp; "
        f"Total Enrolled: {course.total_students}",
        subtitle_style
    ))
    story.append(Spacer(1, 16))

    # Table Header
    table_data = [[
        Paragraph("Student ID", table_header_style),
        Paragraph("Student Name", table_header_style),
        Paragraph("Assignment", table_header_style),
        Paragraph("Score / Max", table_header_style),
        Paragraph("Status", table_header_style),
        Paragraph("Submission Date", table_header_style),
    ]]

    submissions = Submission.objects.filter(assignment__course=course).select_related(
        'student', 'assignment'
    ).order_by('student__last_name', 'assignment__title')

    if submissions.exists():
        for sub in submissions:
            status_text = "Late" if sub.is_late else "On Time"
            score_text = f"{sub.score}/{sub.assignment.max_points}" if sub.score is not None else "Pending"

            table_data.append([
                Paragraph(sub.student.academic_id or "—", cell_style),
                Paragraph(sub.student.get_full_name_or_username(), cell_style),
                Paragraph(sub.assignment.title, cell_style),
                Paragraph(score_text, cell_style),
                Paragraph(status_text, cell_style),
                Paragraph(sub.submitted_at.strftime('%Y-%m-%d'), cell_style),
            ])
    else:
        table_data.append([
            Paragraph("—", cell_style),
            Paragraph("No recorded submissions", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
        ])

    table = Table(table_data, colWidths=[70, 130, 170, 65, 55, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F3E30')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAF9')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E1E9E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(table)
    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="UnivLMS_{course.course_code}_Grades_{timestamp}.pdf"'
    return response

def export_student_transcript_pdf(student):
    """
    Generate an individual student grade transcript report in PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0A291F')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#576860'),
        leading=14
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11
    )

    story = []
    story.append(Paragraph("UnivLMS Official Academic Transcript", title_style))
    story.append(Paragraph(
        f"<b>Student:</b> {student.get_full_name_or_username()} &nbsp;|&nbsp; "
        f"<b>Academic ID:</b> {student.academic_id or 'N/A'} &nbsp;|&nbsp; "
        f"<b>Email:</b> {student.email}",
        subtitle_style
    ))
    story.append(Paragraph(
        f"Generated on {timezone.now().strftime('%B %d, %Y at %H:%M UTC')}",
        subtitle_style
    ))
    story.append(Spacer(1, 16))

    table_data = [[
        Paragraph("Course Code", table_header_style),
        Paragraph("Course Title", table_header_style),
        Paragraph("Assignment", table_header_style),
        Paragraph("Score", table_header_style),
        Paragraph("Max Points", table_header_style),
        Paragraph("Grade", table_header_style),
    ]]

    submissions = Submission.objects.filter(student=student).select_related(
        'assignment', 'assignment__course'
    ).order_by('assignment__course__course_code')

    if submissions.exists():
        for sub in submissions:
            pct_val = (sub.score / sub.assignment.max_points * 100) if sub.score is not None and sub.assignment.max_points else None
            grade_str = f"{pct_val:.1f}%" if pct_val is not None else "Pending"
            score_str = f"{sub.score:.2f}" if sub.score is not None else "Pending"

            table_data.append([
                Paragraph(sub.assignment.course.course_code, cell_style),
                Paragraph(sub.assignment.course.title, cell_style),
                Paragraph(sub.assignment.title, cell_style),
                Paragraph(score_str, cell_style),
                Paragraph(str(sub.assignment.max_points), cell_style),
                Paragraph(grade_str, cell_style),
            ])
    else:
        table_data.append([
            Paragraph("—", cell_style),
            Paragraph("No completed graded assignments found", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
        ])

    table = Table(table_data, colWidths=[70, 160, 160, 60, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F3E30')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAF9')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E1E9E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(table)
    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="Transcript_{student.username}_{timestamp}.pdf"'
    return response
