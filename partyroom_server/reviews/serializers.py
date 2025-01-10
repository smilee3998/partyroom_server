from booking.models import Booking
from error_code_list import *
from main.models import PartyRoom
from rest_framework import serializers
from booking.constants import *
from .models import PartyRoomReview
from utils.utils import now


class ReviewDetailNotProviedError(Exception):
    pass


class PartyRoomReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(source="reviewer.username")
    reviewer_icon_num = serializers.IntegerField(source='reviewer.icon_num')
    
    class Meta:
        model = PartyRoomReview
        fields = (
            "partyroom",
            "rating",
            "comments",
            "reviewer",
            "recommend",
            "updated_at",
            'reviewer_icon_num'
        )

class CreateReviewPermissionSerializer(serializers.Serializer):
    partyroom_uid = serializers.CharField()
    
    
class CreateReviewSerializer(serializers.ModelSerializer):
    partyroom_uid = serializers.CharField(        
            error_messages = {
            'required': PARTYROOM_UID_NOT_PROVIED_ERROR
        })
    is_check =serializers.BooleanField(required=True)
    class Meta:
        model = PartyRoomReview
        fields = (
            'uid', 
            "partyroom_uid",
            "rating",
            "comments",
            "recommend",
            'is_check'
        )
        extra_kwargs = {
            'rating': {
                'required': False
            },
            'comments': {
                'required': False
            },
            'recommend': {
                'required': False
            }
        }
        
    def validate_partyroom_uid(self, value):
        try:
            # cache the partyroom instance for future use
            self.partyroom_instance = PartyRoom.objects.get(uid=value)
            return value
        
        except PartyRoom.DoesNotExist:
            raise serializers.ValidationError(PARTY_ROOM_DOES_NOT_EXIST_ERROR)
           
    # def validate_booking_uid(self, value):
    #     try:
    #         # cache the booking instance for future use
    #         self.booking_instance = Booking.objects.get(uid=value)
            
    #         # check this booking is from this user
    #         user =  self.context['request'].user
    #         if self.booking_instance.user != user:
    #             raise serializers.ValidationError(BOOKING_NOT_BELONG_USER_ERROR_CODE)
    #         return value
            
    #     except Booking.DoesNotExist:
    #         raise serializers.ValidationError(REVIEW_BOOKING_DOES_NOT_EXIST_ERROR_CODE)
        
        
    def validate(self, data):
        # check the user has written the review for this booking before
        self.reviewer =  self.context['request'].user
        bookings = Booking.objects.filter(partyroom=self.partyroom_instance,
                                    user=self.reviewer,
                                    status__in=BOOKING_VALID_STATUS,
                                    start_time__lte=now()).order_by('start_time')
        
        if not bookings.exists():
            # User does not booked this room before 
            raise serializers.ValidationError(NO_RELATIVE_BOOKING_FOUND_ERROR)
        
        self.latest_booking = bookings.first()
        reviews = PartyRoomReview.objects.filter(booking=self.latest_booking)

        if reviews.exists():
            # Always use the lastest booking to write the review
            # if such review exist, then the user cannot write a new review
            raise serializers.ValidationError(SINGLE_REVIEW_ONLY_ERROR_CODE)
        
        return data

    def create(self, validated_data):
        if 'rating' not in validated_data.keys() or \
            'comments' not in validated_data.keys() or \
            'recommend' not in validated_data.keys():
                raise ReviewDetailNotProviedError(f'only {validated_data.keys()} is provided')
        _ = validated_data.pop('partyroom_uid')
        _ = validated_data.pop('is_check')
        
        return PartyRoomReview.objects.create(reviewer=self.reviewer, 
                                              booking=self.latest_booking,
                                              partyroom=self.partyroom_instance,
                                              **validated_data)
