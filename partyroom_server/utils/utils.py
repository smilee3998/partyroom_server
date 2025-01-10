# dulpicated
from datetime import datetime, timedelta, timezone
from logging import getLogger

from booking.models import Booking
from booking.constants import *
from main.models import PartyRoom
from reviews.models import PartyRoomReview

logger = getLogger('utils')

utc = timezone(timedelta(0))
utc8 = timezone(timedelta(hours=8))

def now() -> datetime:
    return datetime.now(utc8)


def check_write_review_permissions(request):
    try:
        uid = request.data['partyroom_uid']
        partyroom = PartyRoom.objects.get(uid=uid)
    except PartyRoom.DoesNotExist:
        logger.error(f"partyroom with {uid=} doesn't exist")
        return False
    except KeyError:
        logger.error('uid haven"t provided')
        return False
    user = request.user
    bookings = Booking.objects.filter(partyroom=partyroom,
                                      user=user,
                                      status__in=BOOKING_VALID_STATUS,
                                      start_time__lte=now()).order_by('start_time')

    if not bookings.exists():
        # User does not booked this room before
        logger.info(f"user does not booked this room before")
        return False
    else:
        latest_booking_id = bookings.first().id
        reviews = PartyRoomReview.objects.filter(booking=latest_booking_id)
        # Always use the lastest booking to write the review
        # if such review exist, then the user cannot write a new review
        return reviews.exists()

