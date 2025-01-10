import random
from datetime import timedelta

from utils.utils import now

UNUSED = 1
USED = 2
FAIL = 3

OTP_REQUEST_TYPE = (
    ('FP', 'Forgot password'),
    ('VE', 'Verify email'),
    ('VI', 'Verify identity')
)

OTP_STATUS_CHOICES = (
    (UNUSED, 'Unused'),
    (USED, 'Used'),
    (FAIL, 'Fail'),
)

RESEND_SEPERATION_MIN = timedelta(minutes=5)
class OTPExistError(Exception):
    """OTP with same type and user exists in db (requests otp should only call once)
    """
    pass


def update_otp(otp_obj) -> None:
    """update expires time and otp code
    """
    otp_obj.expires_at = compute_expires_time()
    otp_obj.otp_code = generate_otp_code()
    otp_obj.save()

def compute_expires_time():
    # default expire time is 5 mins
    return now() + timedelta(seconds=60*5)


def generate_otp_code():
    return random.randint(100000, 999999)

def random_icon_num() -> int:
    return random.randint(1, 10)
