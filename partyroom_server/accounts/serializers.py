import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_serializer
from error_code_list import *
from main.models import PartyRoom
from main.serializers import PartyRoomSerializer
from phonenumber_field.serializerfields import \
    PhoneNumberField as PPhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import OTP
from .utils import *

logger = logging.getLogger(__name__)
User = get_user_model()

def is_existing_email(value):
    """a email is validate if the user with that email exists
    """
    user = User.objects.filter(email=value)
    if not user.exists():
        raise serializers.ValidationError(
            VERIFY_EMAIL_NOT_EXIST_ERROR_CODE)
    return value


class PhoneNumberField(PPhoneNumberField):
    default_error_messages = {'required': PHONE_NUM_NOT_GIVEN_ERROR_CODE,
                              'invalid_phone_number': PHONE_NUM_INVALID_ERROR_CODE,
                              'invalid': PHONE_NUM_INVALID_ERROR_CODE,
                              }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = UniqueValidator(queryset=User.objects.all(), message=PHONE_NUM_EXIST_ERROR_CODE)
        self.validators.append(validator)


class EmailCreateField(serializers.EmailField):
    default_error_messages = {'required': EMAIL_NOT_GIVEN_ERROR_CODE,
                              'invalid': EMAIL_INVALID_ERROR_CODE
                              }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        unique_validator = UniqueValidator(
            queryset=User.objects.all(), message=EMAIL_EXIST_ERROR_CODE)
        self.validators.append(unique_validator)


class CustomUserSerializer(serializers.ModelSerializer):
    favourites = PartyRoomSerializer(read_only=True, many=True)
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(),
                                                                 message=USER_NAME_EXIST_ERROR_CODE), ],
                                     error_messages={
        'required': USER_NAME_NOT_GIVEN_ERROR_CODE,
    })
    phone_number = PhoneNumberField()
    email = EmailCreateField()
    # TODO return booking history
    class Meta:
        model = User
        fields = (
            'uid',
            'username',
            'password',
            'phone_number',
            'email',
            'is_roomer',
            'is_verified',
            'favourites',
            'icon_num',
        )

        extra_kwargs = {
            'uid': {
                'read_only': True
            },
            'password': {
                'write_only': True
            },
            'email': {
                'error_messages': {
                    'required': EMAIL_NOT_GIVEN_ERROR_CODE,
                    'invalid': EMAIL_INVALID_ERROR_CODE
                },
                'required': True
            },
            'is_roomer': {
                'error_messages': {
                    'invalid': IS_ROOMER_INVALID_ERROR_CODE
                },
            },
            'is_verified': {
                'read_only': True
            },
            'icon_num': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    # a serializer for updating the user information other than the password and favourites
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(),
                                                                 message=USER_NAME_EXIST_ERROR_CODE), ],
                                     required=False)
    phone_number = PhoneNumberField(required=False)
    email = EmailCreateField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'phone_number',
            'email',
        )


class RegisterErrorResponseSerializer(serializers.ModelSerializer):
    # For doc only
    status = serializers.ListField(
        child=serializers.CharField(default='ERROR-0000')
    )

    class Meta:
        model = User
        fields = ('status',)


class UserfavouritesSerializer(serializers.ModelSerializer):
    # a serializer for getting the user favourites
    favourites = PartyRoomSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('favourites',)


class UserfavouritesUpdateSerializer(serializers.ModelSerializer):
    # a serializer for updating the user favourites
    favourites = serializers.ListField(
        child=serializers.CharField(default='ABC'),
        required=True,
        error_messages={
            "required": PARTY_ROOM_UID_DOES_NOT_INCLUDE_ERROR,
        }
    )

    class Meta:
        model = User
        fields = ('favourites',)

    def validate_favourites(self, value):
        """check the partyroom uid in favourites list is exist

        Args:
            value (List[str]): a list of partyroom uid

        Raises:
            PARTY_ROOM_UID_FIELD_EMPTY_ERROR: the uid field is empty list []
            PARTY_ROOM_DOES_NOT_EXIST_ERROR: the uid is not valid

        Returns:
            List[str]: a validated list of partyroom uid
        """
        if len(value) == 0:
            raise serializers.ValidationError(PARTY_ROOM_UID_FIELD_EMPTY_ERROR)

        for partyroom_uid in value:
            if not PartyRoom.objects.filter(uid=partyroom_uid).exists():
                raise serializers.ValidationError(
                    PARTY_ROOM_DOES_NOT_EXIST_ERROR)
        return value


class UserfavouritesDeleteSerializer(serializers.ModelSerializer):
    # a serializer for updating the user favourites
    favourites = serializers.ListField(
        child=serializers.CharField(default='ABC'),
        required=True,
        error_messages={
            "required": PARTY_ROOM_UID_DOES_NOT_INCLUDE_ERROR,
        }
    )

    class Meta:
        model = User
        fields = ('favourites',)

    def validate_favourites(self, value):
        """check the partyroom uid in favourites list is exist

        Args:
            value (List[str]): a list of partyroom uid

        Raises:
            PARTY_ROOM_UID_FIELD_EMPTY_ERROR: the uid field is empty list []
            PARTY_ROOM_DOES_NOT_EXIST_ERROR: the uid is not valid
            PARTY_ROOM_UID_NOT_IN_USER_FAVOURITES_ERROR: the valid partyroom uid is not in the user favourites list

        Returns:
            List[str]: a validated list of partyroom uid
        """
        if len(value) == 0:
            raise serializers.ValidationError(PARTY_ROOM_UID_FIELD_EMPTY_ERROR)

        user = self.context['request'].user

        for partyroom_uid in value:
            if not PartyRoom.objects.filter(uid=partyroom_uid).exists():
                raise serializers.ValidationError(
                    PARTY_ROOM_DOES_NOT_EXIST_ERROR)
            elif not PartyRoom.objects.get(uid=partyroom_uid) in user.favourites.all():
                raise serializers.ValidationError(
                    PARTY_ROOM_UID_NOT_IN_USER_FAVOURITES_ERROR)
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True,
                                         error_messages={
                                             "required": OLD_PASSWORD_DOES_NOT_PROVIDE_ERROR,
                                             "blank": OLD_PASSWORD_DOES_NOT_PROVIDE_ERROR
                                         })
    new_password = serializers.CharField(required=True,
                                         error_messages={
                                             "required": NEW_PASSWORD_DOES_NOT_PROVIDE_ERROR,
                                             "blank": NEW_PASSWORD_DOES_NOT_PROVIDE_ERROR
                                         })

    class Meta:
        model = User
        fields = ('old_password', 'new_password',)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                OLD_PASSWORD_DOES_NOT_MATCH_ERROR)
        return value

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class UserEmailSerializer(serializers.ModelSerializer):
    """nested serializer for accessing email of user 
    """
    class Meta:
        model = User
        fields = ('email',)
        extra_kwargs = {
            # remove the auto-generate unique validators
            'email': {'validators': [is_existing_email]}
        }

    def validate(self, data):
        # return a user object instead of email
        user = User.objects.get(email=data['email'])
        return user


class OTPCodeField(serializers.CharField):
    default_error_messages = {'required': OTP_CODE_NOT_GIVEN_ERROR_CODE,
                              'invalid': OTP_INCORRECT_ERROR_CODE,
                              'blank': OTP_CODE_BLANK_ERROR_CODE,
                              'expired': OTP_EXPIRES_ERROR_CODE
                              }


class OTPUidField(serializers.CharField):
    default_error_messages = {'required': OTP_UID_NOT_GIVEN_ERROR_CODE,
                              'invalid': OTP_INEXIST_ERROR_CODE,
                              'blank': OTP_UID_BLANK_ERROR_CODE,
                              }

    def is_existing_otp_uid(self, value):
        otp_objs = OTP.objects.filter(uid=value)
        if not otp_objs.exists():
            raise serializers.ValidationError(self.error_messages['invalid'])
        return value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(self.is_existing_otp_uid)


class OTPTypeField(serializers.ChoiceField):
    default_error_messages = {"invalid_choice": OTP_TYPE_CHOICE_ERROR_CODE,
                              "required": OTP_TYPE_NOT_GIVEN_ERROR_CODE,
                              'not_match': OTP_TYPE_NOT_MATCH_ERROR_CODE,
                              'not_allow': OTP_TYPE_NOT_ALLOW_ERROR_CODE
                              }

    def is_valid_otp_types(self, value):
        if value not in self.valid_otp_types and value in self.choices:
            self.fail('not_allow')
        elif value not in self.choices:
            self.fail('invalid_choice')
        return value

    def __init__(self, valid_otp_types, choices=OTP_REQUEST_TYPE, **kwargs):
        self.valid_otp_types = valid_otp_types
        super().__init__(choices, **kwargs)
        self.validators.append(self.is_valid_otp_types)


class OTPBaseSerializer(serializers.Serializer):
    """Serializer that handle the OTP action and field
    Raises:
        ValueError: otp_type field should be added in order to use this serializer
    """
    otp_code = OTPCodeField(required=True)
    otp_uid = OTPUidField(required=True)

    def __init__(self, instance=None, data=..., **kwargs):
        if self.fields.get('otp_type') is None:
            raise ValueError('otp type should be provided when initializing')

        super().__init__(instance, data, **kwargs)

    def verifiy_otp(self, data):
        otp_code = data.get('otp_code')
        otp_uid = data.get('otp_uid')
        otp_type = data.get('otp_type')
        fields = self.get_fields()

        otp_obj = OTP.objects.get(uid=otp_uid)

        if otp_obj.otp_code != otp_code:
            fields['otp_code'].fail("invalid")

        if otp_obj.otp_type != otp_type:
            fields['otp_type'].fail('not_match')

        if otp_obj.is_expired:
            otp_obj.status = FAIL
            otp_obj.save()
            fields['otp_code'].fail('expired')
        
        if otp_obj.status == USED:
            # OTP can only use once
            raise serializers.ValidationError(OTP_ALREADY_USED_ERROR_CODE)

        otp_obj.status = USED
        otp_obj.save()
        return data

    def validate(self, data):
        data = self.verifiy_otp(data)
        data = super().validate(data)
        return data


class VerifyOTPBaseSerializer(OTPBaseSerializer):
    user = UserEmailSerializer()

    def validate(self, data):
        user = data.get('user')
        otp_uid = data.get('otp_uid')
        otp_obj = OTP.objects.get(uid=otp_uid)

        if otp_obj.user != user:
            # should be the same user that create this otp
            raise serializers.ValidationError(NOT_USER_OWN_OTP_ERROR_CODE)

        data = super().validate(data)
        return data


class VerifyOTPSerializer(VerifyOTPBaseSerializer):
    otp_type = OTPTypeField(required=True, valid_otp_types=['VE', 'VI'])


class RequestOTPSerializer(serializers.ModelSerializer):
    user = UserEmailSerializer()
    otp_type = OTPTypeField(required=True, valid_otp_types=['VE', 'VI'])

    def validate(self, data):
        user = data.get('user')
        if user.is_verified and data['otp_type'] == 'VE':
            raise serializers.ValidationError(USER_ALREADY_VERIFIED_ERROR_CODE)

        return data

    class Meta:
        model = OTP
        fields = ('user', 'otp_type', 'uid', 'expires_at',)
        extra_kwargs = {
            'uid': {
                'read_only': True
            },
            'expires_at': {
                'read_only': True
            },
        }


class ResendOTPSerializer(serializers.ModelSerializer):
    uid = serializers.CharField()  # uid field in model is read only

    def validate_uid(self, value):
        otp_obj = OTP.objects.filter(uid=value)
        if not otp_obj.exists():
            raise serializers.ValidationError(OTP_INEXIST_ERROR_CODE)
        elif otp_obj.otp_type == 'FP':
            # forgot password FP cannot resend
            raise serializers.ValidationError(OTP_TYPE_NOT_ALLOW_ERROR_CODE)
        return value

    class Meta:
        model = OTP
        fields = ('uid', 'expires_at',)
        extra_kwargs = {
            'expires_at': {
                'read_only': True
            },
        }


class ForgotPasswordSerializer(VerifyOTPBaseSerializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'}
    )
    otp_type = OTPTypeField(required=True, valid_otp_types=['FP'])

    def validate(self, data):
        data = super().validate(data)
        user = data['user']
        if not user.is_verified:
            # only verified user can forgot password
            raise serializers.ValidationError(NON_VERIFIED_USER_ERROR_CODE)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.validated_data['user']

        user.set_password(password)
        user.save()
        return user
    

class UserLoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'is_staff',)
        
