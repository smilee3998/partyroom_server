from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from shortuuidfield import ShortUUIDField

STATUS_CHOICES = (
    ('PENDING', 'pending'),
    ('TRANSITION', 'transition'),
    ('PAID', 'paid'),
    ('CONFIRM', 'confirm'),
    ('REJECTED', 'rejected'),
    ('CANCELED', 'canceled'),
    ('OUTDATED', 'outdated'),
    ('NOT_OPEN', 'not_open'),   
)

def increment_booking_id():
    last_booking = Booking.objects.all().order_by('id').last()
    return 100000 if not last_booking else last_booking.id + 1


class Booking(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        editable=False,
    )
    uid = ShortUUIDField(
        unique=True, 
    )
    partyroom = models.ForeignKey(
        to='main.partyroom',
        on_delete=models.CASCADE,
        verbose_name='partyroom', 
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='user'
    )
    start_time = models.DateTimeField(
        verbose_name='booking start time',
    )
    end_time = models.DateTimeField(
        verbose_name='booking end time',
    )
    # TODO replace char by positve integer
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=10,
        verbose_name='booking status',
        default='pending'
    )
    num_users = models.PositiveIntegerField(
        default=1,
        validators=[MaxValueValidator(999)],
        verbose_name='number of users',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='booking created date',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='booking last update date',
    )
    unit_price = models.PositiveIntegerField(
        verbose_name='booking unit price'
    )
    total_price = models.PositiveIntegerField(
        verbose_name='booking total price'
    )
    
    def __str__(self):
        return f'{self.partyroom.uid} {str(self.start_time)[:16]}-{str(self.end_time)[:16]}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.id = increment_booking_id()
        super(Booking, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)    