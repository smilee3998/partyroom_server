import logging
from datetime import timedelta

from error_code_list import *
from main.models import PartyRoom
from main.serializers import PartyRoomBriefImageSerializer, PartyRoomBriefSerializer
from rest_framework import serializers

from .constants import BOOKING_UNAVAILABLE_STATUS
from .models import Booking


logger = logging.getLogger(__name__)


class BookingReserveSerializer(serializers.ModelSerializer):
    partyroom = serializers.CharField(max_length=3)
    # TODO cannot reserve the days that have passed
    class Meta:
        model = Booking
        fields = ('partyroom', 'start_time', 'end_time', 'num_users', 'unit_price', 'total_price', 'uid')
        extra_kwargs = {
            'num_users': {
                'error_messages': {
                    'invalid': BOOKING_NUM_USERS_INVALID_TYPE_ERROR
                }
            },
            'start_time': {
                'error_messages': {
                    'invalid': BOOKING_START_TIME_INVALID_ERROR
                }
            },
            'end_time': {
                'error_messages': {
                    'invalid': BOOKING_END_TIME_INVALID_ERROR
                }
            },
            'unit_price': {
                'error_messages': {
                    'invalid': BOOKING_UNIT_PRICE_INVALID_TYPE_ERROR
                }
            },
            'total_price': {
                'error_messages': {
                    'invalid': BOOKING_TOTAL_PRICE_INVALID_TYPE_ERROR
                }
            }
        }
    def validate_num_users(self, value):
        if not 0 < value <= 999:
            raise serializers.ValidationError(BOOKING_NUM_USERS_INVALID_ERROR)
        return value
    
    def validate_unit_price(self, value):
        if value < 0 :
            raise serializers.ValidationError(BOOKING_UNIT_PRICE_INVALID_ERROR)
        return value
    
    def validate_total_price(self, value):
        if value < 0 :
            raise serializers.ValidationError(BOOKING_TOTAL_PRICE_INVALID_ERROR)
        return value

    def validate_partyroom(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError(BOOKING_UID_TYPE_ERROR)
        try:
            partyroom = PartyRoom.objects.get(uid=value)
            # return partroom instance instead of partyroom uid
            return partyroom
        
        except PartyRoom.DoesNotExist:
            raise serializers.ValidationError(BOOKING_UID_DOES_NOT_EXIST_ERROR)     
            
    def create(self, validated_data):
        return Booking.objects.create(**validated_data, status='confirm')  # BETA
    
    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        partyroom = data.get('partyroom')
        if start_time >= end_time:
            # start time is later than end time
            raise serializers.ValidationError(BOOKING_START_TIME_GTE_END_TIME_ERROR)
        
        # case1 this booking start before an existing booking but end time is overlapped to an existing booking
        conflict_bookings_case1 = Booking.objects.filter(start_time__gte=start_time,
                                                         start_time__lt=end_time, 
                                                         partyroom__uid=partyroom.uid,
                                                         status__in=BOOKING_UNAVAILABLE_STATUS)
        if len(conflict_bookings_case1) != 0:
            raise serializers.ValidationError(BOOKING_TIME_CONFLICS_CASE1_ERROR)
                                                         
        # case2 this booking start within an existing booking period but end after the existing bookin      
        conflict_bookings_case2 = Booking.objects.filter(end_time__gt=start_time, 
                                                   end_time__lte=end_time,
                                                   partyroom__uid=partyroom.uid,
                                                   status__in=BOOKING_UNAVAILABLE_STATUS)
        if len(conflict_bookings_case2) != 0:
            raise serializers.ValidationError(BOOKING_TIME_CONFLICS_CASE2_ERROR)  
              
        # case 3 this booking is within an existing booking time period
        conflict_bookings_case3 = Booking.objects.filter(start_time__lte=start_time, 
                                                   end_time__gte=end_time,
                                                   partyroom__uid=partyroom.uid,
                                                   status__in=BOOKING_UNAVAILABLE_STATUS)
        if len(conflict_bookings_case3) != 0:
            raise serializers.ValidationError(BOOKING_TIME_CONFLICS_CASE3_ERROR)   
             
        # case 4 this booking includes an existing booking period
        conflict_bookings_case4 = Booking.objects.filter(start_time__gte=start_time,
                                                         end_time__lte=end_time,
                                                         partyroom__uid=partyroom.uid,
                                                         status__in=BOOKING_UNAVAILABLE_STATUS)
        if len(conflict_bookings_case4) != 0:
            raise serializers.ValidationError(BOOKING_TIME_CONFLICS_CASE4_ERROR)

        return data
    

class AvailableBookingListSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M')
    end_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M')
    
    class Meta:
          model = Booking
          fields = ('start_time', 'end_time',)          


class BookingCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('uid',)
        lookup_field = 'uid'
        

class BookingDetailSerializer(serializers.ModelSerializer):
    partyroom = PartyRoomBriefSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ('uid', 'start_time', 'end_time', 'num_users', 'status', 'partyroom')
        read_only_fields = ('status',)
           
class BookingListSerializer(serializers.ModelSerializer):
    partyroom = PartyRoomBriefImageSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ('uid', 'start_time', 'end_time', 'status', 'partyroom')
