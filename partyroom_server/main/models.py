import base64
import logging

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_mysql.models import ListTextField, SizedTextField

from .utils import *

logger = logging.getLogger(__name__)


def increment_partyroom_id():
    last_partyroom = PartyRoom.objects.all().order_by('id').last()
    return 1 if not last_partyroom else last_partyroom.id + 1



class PartyRoom(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        editable=False,
    )
    owner = models.ForeignKey(
        to='accounts.CustomUser',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=20
    )
    uid = models.CharField(
        max_length=3,
        unique=True
    )
    area = models.CharField(
        max_length=3,
        choices=AREA_CHOICES,
        default='KWN',
    )
    district = models.CharField(
        max_length=3,
        choices=DISTRICT_CHOICES,
        default='KT',
    )
    fullAddress = SizedTextField(
        blank=True,
        null=True,
        size_class=2
    )
    transitionTime = models.PositiveIntegerField(
        default=15,
        help_text="transition time between booking in minutes"
    )

    # todo imageSets
    minNumUsers = models.PositiveIntegerField(
        default=1,
        validators=[MaxValueValidator(999), MinValueValidator(1)]
    )
    maxNumUsers = models.PositiveIntegerField(
        default=10,
        validators=[MaxValueValidator(999), MinValueValidator(1)]
    )
    shortDesp = models.CharField(
        blank=True,
        null=True,
        max_length=MAX_SHORT_DESCRIPTION_LENGTH
    )
    description = SizedTextField(
        blank=True,
        null=True,
        size_class=2
    )
    ruleList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_RULES,
        blank=True
    )
    venueFaciList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_VENUE_FACI,
        blank=True
    )
    entertainFaciList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_ENTERTAIN_FACI,
        blank=True
    )
    gameList = models.JSONField(
        default=dict
    )
    boardgameList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_BOARDGAME,
        blank=True
    )
    addtionalServiceList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_BOARDGAME,
        blank=True
    )
    chargeList = models.JSONField(
        default=dict
    )
    bookingMethodList = ListTextField(
        base_field=models.CharField(max_length=1000),
        size=MAX_NUM_BOARDGAME,
        blank=True
    )
    transportList = models.JSONField(
        default=dict
    )
    @property
    def image_cover(self) -> Optional[str]:
        try:
            image_path = get_image_cover_path(self.uid)
            if image_path is not None:
                with open(image_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            else:
                temp_image_path = get_image_cover_path('YUX')
                with open(temp_image_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
                 
        except Exception as e:
            logger.error(e)
            return None

    @property
    def rating_stars(self) -> float:
        return cal_rating(self.id)
    
    @property
    def image_cover_last_mt(self) -> datetime:
        return get_image_last_update_time(self.uid)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.id = increment_partyroom_id()
        if not self.uid:
            self.uid = id_generator()
            while PartyRoom.objects.filter(uid=self.uid).exists():
                self.uid = id_generator()
        super(PartyRoom, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)
