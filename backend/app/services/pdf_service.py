import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFService:

    @staticmethod
    def generate_student_report_pdf(student_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1E1B4B'), spaceAfter=12)
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#4B5563'), spaceAfter=18)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#312E81'), spaceAfter=8)

        story.append(Paragraph("EduNexus — Official Academic Performance Report", title_style))
        story.append(Paragraph(f"Student: <b>{student_data.get('student_name')}</b> | Roll No: <b>{student_data.get('roll_number')}</b> | Dept: <b>{student_data.get('department_name')}</b>", subtitle_style))
        story.append(Spacer(1, 10))

        # Academic Summary Table
        summary_data = [
            ["Metric", "Value"],
            ["Cumulative GPA (CGPA)", f"{student_data.get('cgpa')}"],
            ["Overall Attendance", f"{student_data.get('overall_attendance')}%"],
            ["Assignment Completion Rate", f"{student_data.get('assignment_completion_rate')}%"],
            ["Academic Risk Status", str(student_data.get('risk_status')).upper()]
        ]

        t_summary = Table(summary_data, colWidths=[240, 240])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#312E81')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, -1), 8),
            ('TOPPADDING', (0, 0), (1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 20))

        # Attendance Breakdown Table
        story.append(Paragraph("Course-wise Attendance Breakdown", section_style))
        att_data = [["Course Code", "Course Name", "Attended / Total", "Percentage"]]
        for item in student_data.get('attendances_by_course', []):
            att_data.append([
                item.get('course_code'),
                item.get('course_name'),
                f"{item.get('present')} / {item.get('total')}",
                f"{item.get('percentage')}%"
            ])

        t_att = Table(att_data, colWidths=[100, 200, 100, 80])
        t_att.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4C1D95')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_att)
        story.append(Spacer(1, 20))

        # Risk Summary Notes
        story.append(Paragraph("AI Decision-Support Remarks", section_style))
        story.append(Paragraph(student_data.get('risk_summary', 'No specific risk remarks.'), styles['Normal']))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @staticmethod
    def generate_student_report_csv(student_data: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["EDUNEXUS ACADEMIC PERFORMANCE REPORT"])
        writer.writerow(["Student Name", student_data.get('student_name')])
        writer.writerow(["Roll Number", student_data.get('roll_number')])
        writer.writerow(["Department", student_data.get('department_name')])
        writer.writerow(["CGPA", student_data.get('cgpa')])
        writer.writerow(["Overall Attendance (%)", student_data.get('overall_attendance')])
        writer.writerow(["Assignment Completion (%)", student_data.get('assignment_completion_rate')])
        writer.writerow(["Risk Status", student_data.get('risk_status')])
        writer.writerow([])

        writer.writerow(["COURSE-WISE ATTENDANCE"])
        writer.writerow(["Course Code", "Course Name", "Present", "Total", "Percentage"])
        for item in student_data.get('attendances_by_course', []):
            writer.writerow([
                item.get('course_code'),
                item.get('course_name'),
                item.get('present'),
                item.get('total'),
                item.get('percentage')
            ])

        return output.getvalue()
