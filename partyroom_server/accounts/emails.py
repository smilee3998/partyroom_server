import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import OTP, CustomUser

logger = logging.getLogger(__name__)

def get_email_subject(email_type: str):
    if email_type == 'VE':
        subject = 'Partyroom account email verification'
    elif email_type == 'VI':
        subject = 'Partyroom account reset password verification'
    else:
        raise ValueError(f'unknown type {email_type=}')
    return subject

def _send_email(subject, message, email):
    email_from = settings.EMAIL_HOST
    if 'example' not in email and 'email' not in email:
        send_mail(subject, message, email_from, [email])
    else:
        logger.info(f'Not send to {email=}')
    
def send_otp_via_email(email, email_type, otp_code):
    subject = get_email_subject(email_type)
    message = f'Your otp is {otp_code}'
    
    _send_email(subject, message, email)


def resend_otp_via_email(otp_obj: OTP):
    
    email_type = otp_obj.otp_type
    email = otp_obj.user.email
    subject = get_email_subject(email_type)
    
    message = f'Your otp is {otp_obj.otp_code}'
    
    _send_email(subject, message, email)
    return otp_obj