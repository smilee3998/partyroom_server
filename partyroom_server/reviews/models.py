from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from error_code_list import *
from shortuuidfield import ShortUUIDField


class PartyRoomReview(models.Model):
    partyroom = models.ForeignKey(
        to='main.partyroom',
        on_delete=models.CASCADE,
        verbose_name='partyroom',
    )
    reviewer = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='user'
    )
    booking = models.ForeignKey(
        to='booking.Booking',
        on_delete=models.CASCADE,
        verbose_name='relative booking'
    )
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)], verbose_name="Rating from 0 to 5")
    comments = models.TextField(max_length=1000, blank=True, verbose_name="Comments")
    recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uid = ShortUUIDField(
        unique=True, 
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        
