from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from main.models import PartyRoom
from phonenumber_field.modelfields import PhoneNumberField
from shortuuidfield import ShortUUIDField

from utils.utils import now

from .utils import *

MAX_FAVOURITES = 1000


def increment_user_id():
    last_user = CustomUser.objects.all().order_by('id').last()
    return 1 if not last_user else last_user.id + 1 

def increment_OTP_id():
    last_otp = OTP.objects.all().order_by('id').last()
    return 100000 if not last_otp else last_otp.id + 1


class CustomUser(AbstractUser):
    REQUIRED_FIELDS = ['phone_number', 'email']
    id = models.PositiveIntegerField(
        primary_key=True,
        editable=False,
        auto_created=True,
    )
    uid = ShortUUIDField(
        unique=True, 
    )
    username = models.CharField(
        _('username'),
        max_length=20,
        unique=True,
        help_text=_('Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )    
    phone_number = PhoneNumberField(
        null=False,
        blank=False,
        unique=True,
    )
    is_roomer = models.BooleanField(
        default=False
    )
    favourites = models.ManyToManyField(
        PartyRoom,
    )
    is_verified = models.BooleanField(default=False)
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), blank=True, unique=True)
    icon_num = models.PositiveSmallIntegerField(default=random_icon_num)
    
    def __str__(self):
        return self.username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.id = increment_user_id()
        super(CustomUser, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)


class OTP(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        editable=False,
    )
    uid = ShortUUIDField(
        unique=True, 
    )
    otp_code = models.CharField(
        max_length=6,
        null=True,
        blank=True,
        default=generate_otp_code
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='user',
        null=False,
        blank=False
    )
    expires_at = models.DateTimeField(
        verbose_name='expires at',
        null=False,
        blank=False,
        default=compute_expires_time
    )
    otp_type = models.CharField(
        max_length=2,
        choices=OTP_REQUEST_TYPE,
        null=False,
        blank=False
    )
    status = models.CharField(
        choices=OTP_STATUS_CHOICES,
        max_length=1,
        verbose_name='OTP status',
        default=1
    )
    last_request = models.DateTimeField(
        verbose_name='last request time',
        auto_now=True
    )
    @property
    def allow_resend(self):
        return self.last_request - now() >  RESEND_SEPERATION_MIN
    
    @property
    def is_expired(self):
        return self.expires_at < now()
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.id = increment_OTP_id()
        super(OTP, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)
    
    def __str__(self):
        return f'{self.otp_code}_user={self.user}'
