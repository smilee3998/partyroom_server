import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

from django.conf import settings
from reviews.models import PartyRoomReview

DISTRICT_CHOICES = (
    ('CW', 'Central and Western'),
    ('WC', 'Wan Chai'),
    ('E', 'Eastern'),
    ('S', 'Southern'),
    ('YTM', 'Yau Tsim Mong'),
    ('SSP', 'ShamS hui Po'),
    ('KC', 'Kowloon City'),
    ('WTS', 'Wong Tai Sin'),
    ('KT', 'Kwun Tong'),
    ('NKT', 'Kwai Tsing'),
    ('TW', 'Tsuen Wan'),
    ('TM', 'Tuen Mun'),
    ('YL', 'Yuen Long'),
    ('N', 'North'),
    ('TP', 'Tai Po'),
    ('ST', 'Sha Tin'),
    ('SK', 'Sai Kung'),
    ('I', 'Islands'),
)

AREA_CHOICES = (
    ('KWN', 'KWN'),
    ('NT', 'NT'),
    ('HKI', 'HKI'),
)

MAX_NUM_RULES = 30
MAX_NUM_VENUE_FACI = 30
MAX_NUM_ENTERTAIN_FACI = 30
MAX_NUM_BOARDGAME = 30
MAX_NUM_ADDITIONAL_SERVICE = 30
MAX_NUM_BOOKING_METHOD = 15
MAX_SHORT_DESCRIPTION_LENGTH = 100


def convert_querystring_to_dict(request) -> Dict:
    query_dict = {}
    for filter_keyword in PARTY_ROOM_FILTERING_LIST:
        value = request.GET.get(filter_keyword)
        if value:
            query_dict[filter_keyword] = value

    return query_dict


def id_generator(size=3, chars=string.ascii_uppercase) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


def convert_to_district_shortcut(district: str) -> Optional[str]:
    for key, val in DISTRICT_CHOICES:
        if val == district:
            return key
    return None

def get_image_cover_path(uid) -> Path:
    path = settings.PARTYROOM_IMAGE_URL / f'{uid}.jpg'
    return path if path.is_file() else None

def mtime_to_iso(mtime):
    return datetime.fromtimestamp(mtime, timezone(timedelta(hours=8)))
 
def get_image_last_update_time(uid):
    image_path = get_image_cover_path(uid)
    last_modify = None
    if image_path.is_file():
        last_modify = image_path.stat().st_mtime
        last_modify = mtime_to_iso(last_modify)
    return last_modify


def get_relative_review(partyroom_id: int):
    return PartyRoomReview.objects.filter(partyroom=partyroom_id)

def cal_rating(partyroom_id: int) -> float:
    reviews = get_relative_review(partyroom_id)
    reviews_count = len(reviews)
    if reviews_count == 0:
        return 0
    
    rating_sum = 0
    for review in reviews:
        rating_sum += review.rating
        
    return rating_sum / reviews_count
    
    
