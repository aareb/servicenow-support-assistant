import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

def send_weekly_report_email(report_path, recipients):
    with open(report_path, 'r') as f:
        report = json.load(f)
    summary = json.dumps(report['summary'], indent=2)
    subject = f"Weekly Incident Report - {report.get('generated_at', '')}"
    body = f"""
Hello,

Please find the weekly incident report below:

Summary by Priority & Status:
{summary}

Best regards,
Support Automation
"""
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_FROM')
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        server.sendmail(msg['From'], recipients, msg.as_string())

if __name__ == '__main__':
    # Example usage: set recipients as needed
    recipients = os.getenv('REPORT_RECIPIENTS', '').split(',')
    send_weekly_report_email('weekly_incident_report.json', recipients)
