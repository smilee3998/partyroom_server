from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Booking
from datetime import date, time, datetime, timedelta
from utils.utils import utc


class BookingUnavailableFilter(filters.FilterSet):
    booking_date = filters.DateFilter(method='booking_date_filter')
    class Meta:
        model = Booking
        fields = ('partyroom__uid', 'booking_date',)
    

    def booking_date_filter(self, queryset, name: str, booking_date: date):
        """filter either start time or end time of existing booking equal to the booking date

        Args:
            queryset ([type]): Booking.objects.all
            name ([type]): name of this field("booking_date")
            booking_date (date): value of the booking date field

        Returns:
            [type]: a queryset
        """
        previous_date = booking_date - timedelta(1)  # day before
        utc_start_booking_datetime = datetime.combine(previous_date, time(hour=16), tzinfo=utc)
        utc_end_booking_datetime = datetime.combine(booking_date, time(hour=16), tzinfo=utc)

        # first query the date, then validate the time(in utc time zone)
        return queryset.filter(Q(start_time__contains=previous_date)).filter(start_time__gte=utc_start_booking_datetime) |  \
                queryset.filter(Q(end_time__contains=booking_date)).filter(end_time__lte=utc_end_booking_datetime)
    