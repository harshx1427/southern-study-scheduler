"""from flask_mail import Message
from app import mail
import os

def send_email(subject, recipients, body):
    msg = Message(
        subject,
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=recipients,
        body=body
    )
    mail.send(msg)
"""