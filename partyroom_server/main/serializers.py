from error_code_list import *
from rest_framework import serializers

from .models import PartyRoom
from .utils import DISTRICT_CHOICES


class DistrictChoiceField(serializers.ChoiceField):
    def to_representation(self, value):
        return self._choices[value]

    def to_internal_value(self, data):
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)

class PartyRoomBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyRoom
        fields =[
            'uid',
            'name',
        ]

class PartyRoomBriefImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyRoom
        fields =(
            'uid',
            'name',
            'image_cover',
            )
        
class PartyRoomSerializer(serializers.ModelSerializer):
    district = DistrictChoiceField(choices=DISTRICT_CHOICES)

    class Meta:
        model = PartyRoom
        fields = (
            'uid',
            'name',
            'area',
            'district',
            'shortDesp',
            'minNumUsers',
            'maxNumUsers',
            'image_cover',
            'rating_stars'
        )
        read_only_fields = ('image_cover', 'rating_stars',)


class PartyRoomDetailSerializer(serializers.ModelSerializer):
    ruleList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': RULE_LIST_NOT_A_LIST_ERROR_CODE
        }
    )
    venueFaciList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': VENUE_LIST_NOT_A_LIST_ERROR_CODE
        }        
    )
    entertainFaciList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': ENTERTAIN_LIST_NOT_A_LIST_ERROR_CODE
        }        
    )
    boardgameList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': BOARD_GAME_LIST_NOT_A_LIST_ERROR_CODE
        }        
    )
    addtionalServiceList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': ADDITIONAL_SERVICE_LIST_NOT_A_LIST_ERROR_CODE
        }        
    )
    bookingMethodList = serializers.ListField(
        child=serializers.CharField(),
        error_messages = {
            'not_a_list': BOOKING_METHOD_LIST_NOT_A_LIST_ERROR_CODE
        }        
    )
    ownerPhoneNo = serializers.StringRelatedField(
        source='owner.phone_number'
    )

    class Meta:
        model = PartyRoom
        fields = (
            "uid",
            "name",
            "minNumUsers",
            "maxNumUsers",
            "area",
            "district",
            "fullAddress",
            "shortDesp",
            "description",
            "ruleList",
            "venueFaciList",
            "entertainFaciList",
            "gameList",
            "boardgameList",
            "addtionalServiceList",
            "chargeList",
            "bookingMethodList",
            "transportList",
            'ownerPhoneNo',
            'image_cover_last_mt',
            'image_cover',
            'rating_stars',
        )
        read_only_fields = (
            'uid',
            'ownerPhoneNo',
            'image_cover_last_mt',
            'rating_stars',
        )
        extra_kwargs = {
            'shortDesp': {
                'write_only': True
            },
            'minNumUsers': {
                'error_messages': {
                    'min_value': MIN_NUM_USERS_MIN_ERROR_CODE,
                    'max_value': MIN_NUM_USERS_MAX_ERROR_CODE,
                    'invalid': MIN_NUM_GTE_MAX_NUM_USERS_ERROR_CODE,
                }
            },
            'maxNumUsers': {
                'error_messages': {
                    'min_value': MAX_NUM_USERS_MIN_ERROR_CODE,
                    'max_value': MAX_NUM_USERS_MAX_ERROR_CODE,
                }
            },
            'district': {
                'error_messages': {
                    'invalid_choice': DISTRICT_INVALID_CHOICE_ERROR_CODE,
                }
            },
            'area': {
                'error_messages': {
                    'invalid_choice': AREA_INVALID_CHOICE_ERROR_CODE,
                }
            },
        }
    def validate_minNumUsers(self, minNumUsers):
        maxNumUsers = self.initial_data.get('maxNumUsers')
        
        if minNumUsers > maxNumUsers:
            raise serializers.ValidationError(MIN_NUM_GTE_MAX_NUM_USERS_ERROR_CODE)
        return minNumUsers
    
    # TODO validate UID
    
    
     
class PartyRoomFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyRoom
        fields = ('uid',)

class PartyRoomImageGetSerializer(serializers.ModelSerializer):
    uid = serializers.CharField(max_length=3, min_length=3, write_only=True)
    class Meta:
        model = PartyRoom
        fields = ('uid', 'image_cover',)
        read_only_fields = ('image_cover', )
        
    def validate_uid(self, value):
        try:
            partyroom = PartyRoom.objects.get(uid=value)
            return value
        
        except PartyRoom.DoesNotExist:
            raise serializers.ValidationError(PARTY_ROOM_DOES_NOT_EXIST_ERROR)  
