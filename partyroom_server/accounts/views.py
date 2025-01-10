import logging
from typing import List

from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from error_code_list import *
from knox.auth import AuthToken
from knox.views import LoginView as KnoxLoginView
from main.models import PartyRoom
from rest_framework import mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveUpdateAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from utils.permissions import *

from .constants import *
from .emails import resend_otp_via_email, send_otp_via_email
from .serializers import *
from .utils import update_otp

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_otp(user, otp_type) -> OTP:
    otp = OTP.objects.filter(user=user, otp_type=otp_type)
    if otp.exists():
        old_otp = otp[0]
        if otp_type == 'FP':
            update_otp(old_otp)
            return old_otp

        elif old_otp.is_expired or old_otp.status == USED or old_otp.status == FAIL:
            # allow user to request again when the old otp is not valid
            update_otp(old_otp)
            return old_otp
        raise OTPExistError

    otp_obj = OTP.objects.create(user=user, otp_type=otp_type)
    return otp_obj


class CustomUserDestoryView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [SafelistPermission, IsOwner, IsAuthenticated, IsNonVerifiedUser]
    lookup_field = 'uid'


class CustomUserCreateView(GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = []


class CustomUserDetailView(RetrieveUpdateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        elif self.request.method in ('PUT', 'PATCH',):
            return CustomUserUpdateSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'GET':
            permission_classes = [IsOwnerOrStaff,
                                  SafelistPermission, IsAuthenticated]
        elif self.request.method in ('PUT', 'PATCH'):
            permission_classes = [IsOwner, SafelistPermission, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self, queryset=None):
        return self.request.user


class UserfavouriteView(GenericViewSet,
                        mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrStaff, IsVerifiedUser,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserfavouritesSerializer
        elif self.action == 'put':
            return UserfavouritesUpdateSerializer
        elif self.action == 'destroy':
            return UserfavouritesDeleteSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        """add each uid in the favourites list to the request.user favourites

        Args:
            request: request from a login user, and a uid list

        Returns:
            Response: either HTTP_200_OK with status Sucessful
            or HTTP_400_BAD_REQUEST with error_code_list
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.action_to_each_favourite(request, request.user.favourites.add)

    def destroy(self, request, *args, **kwargs) -> Response:
        """delete each uid in the favourites list to the request.user favourites

        Args:
            request: request from a login user, and a uid list

        Returns:
            Response: either HTTP_200_OK with status Sucessful
            or HTTP_400_BAD_REQUEST with error_code_list
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.action_to_each_favourite(request, request.user.favourites.remove)

    def action_to_each_favourite(self, request, action) -> Response:
        """loop through the favourites list and perform the given action

        Args:
            request: request from a login user, and a uid list
            method (function): a function that either add or remove the favourite from the user

        Returns:
            Response: either HTTP_200_OK with status Sucessful
            or HTTP_400_BAD_REQUEST with error_code_list
        """
        for partyroom_uid in request.data['favourites']:
            partyroom = PartyRoom.objects.get(uid=partyroom_uid)
            action(partyroom)

        return Response({'status': 'Success'}, status=status.HTTP_200_OK)


class CustomUserChangePasswordView(UpdateAPIView):
    """An endpoint for changing the password
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsVerifiedUser)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if hasattr(user, 'auth_token'):
            logger.debug('has token')
            user.auth_token.delete()
        token, created = AuthToken.objects.get_or_create(user=user)

        return Response({'token': token.key, 'status': 'Success'}, status=status.HTTP_200_OK)


class LoginView(KnoxLoginView):
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer
    
    def login(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class AccountOTPView(GenericViewSet):
    queryset = OTP.objects.all()
    authentication_classes = ()

    def get_serializer_class(self):
        if self.action == 'verify':
            return VerifyOTPSerializer
        elif self.action == 'requests':
            return RequestOTPSerializer
        elif self.action == 'resend':
            return ResendOTPSerializer

    @action(['post'], detail=False, url_name='resend_otp')
    def resend(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_obj = OTP.objects.get(uid=serializer.data['uid'])

        if not otp_obj.allow_resend:
            return Response({'error_code_list': [OTP_REQUEST_TOO_FREQUENT_ERROR_CODE]})
        update_otp(otp_obj)
        resend_otp_via_email(otp_obj)
        read_serializer = self.get_serializer(otp_obj)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False, url_name='requests_otp')
    def requests(self, request, *args, **kwargs):
        """request the otp for either verify email(VE) or verify identity(VI)"""
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        otp_type = serializer.validated_data['otp_type']
        try:
            otp_obj = generate_otp(user, otp_type)
        except OTPExistError:
            # OTP request should only call once
            return Response({'error_code_list': [OTP_REQUEST_TWICE_ERROR_CODE]})

        send_otp_via_email(user.email, otp_type, otp_obj.otp_code)
        read_serializer = self.get_serializer(otp_obj)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False, url_name='verify_otp')
    def verify(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if serializer.data['otp_type'] == 'VE':
            user.is_verified = True
            user.save()

            return Response({'status': 'Success'}, status=status.HTTP_200_OK)

        elif serializer.data['otp_type'] == 'VI':
            otp = generate_otp(user, 'FP')
            return Response({'status': 'Success',
                             'otp_code': otp.otp_code,
                             'otp_uid': otp.uid,
                             },
                            status=status.HTTP_200_OK)
        else:
            raise ValueError(
                f'Wrong type but not handled {serializer.data["otp_type"]=}')


class UserForgotPasswordView(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    authentication_classes = ()

    @action(['post'], detail=False, url_name='forgot_password')
    def forgot_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if hasattr(user, 'auth_token'):
            user.auth_token.delete()

        return Response({'status': 'Success'}, status=status.HTTP_200_OK)

# TODO Change email field
