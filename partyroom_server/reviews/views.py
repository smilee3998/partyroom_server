from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from main.models import PartyRoom
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsBookedUser, IsVerifiedUser, SafelistPermission
from utils.responses import ALLOWED_RESPONSE, REVIEW_DETAIL_NOT_PROVIED_RESPONSE

from .serializers import *



class PartyRoomReviewListView(generics.ListAPIView):
    queryset = PartyRoomReview.objects.all()
    lookup_field = 'party_room_id'
    serializer_class = PartyRoomReviewSerializer
    pagination_class = PageNumberPagination
    authentication_classes = ()
    permission_classes = (SafelistPermission, )
    
    def get_queryset(self):
        room_id = self.kwargs.get(self.lookup_field)
        review_list = PartyRoomReview.objects.filter(partyroom__uid=room_id)
        return review_list

class PartyRoomCreateReviewView(generics.CreateAPIView):
    """User must book this room before, AND the booking time should be passed, AND only one review can be written
    """
    queryset = PartyRoomReview.objects.all()
    serializer_class = CreateReviewSerializer
    permission_classes = (IsAuthenticated, IsVerifiedUser, SafelistPermission, )
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_check = serializer.validated_data['is_check']
        if is_check:
            return ALLOWED_RESPONSE
        return self.create(request, serializer=serializer, *args, **kwargs)
    
    def create(self, request, serializer, *args, **kwargs):
        try:
            self.perform_create(serializer)
        except ReviewDetailNotProviedError:
            return REVIEW_DETAIL_NOT_PROVIED_RESPONSE
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
