import logging

from accounts.models import CustomUser
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.permissions import *

from .filters import PartyRoomFilter, PartyRoomUidFilter
from .models import PartyRoom
from .serializers import (PartyRoomDetailSerializer,
                          PartyRoomImageGetSerializer, PartyRoomSerializer)
from .utils import convert_querystring_to_dict, convert_to_district_shortcut

logger = logging.getLogger(__name__)


class PartyRoomList(generics.ListAPIView):
    # view for listing partyroom
    queryset = PartyRoom.objects.all()
    authentication_classes = ()
    permission_classes = (SafelistPermission,)
    serializer_class = PartyRoomSerializer
    pagination_class = PageNumberPagination
    # TODO UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'main.models.PartyRoom'> QuerySet.

class PartyRoomCreateView(generics.CreateAPIView):
    # view for creating partyroom
    queryset = PartyRoom.objects.all()
    permission_classes = (IsAuthenticated, SafelistPermission, IsRoomerOrStaff, IsVerifiedUser)
    serializer_class = PartyRoomDetailSerializer
    
    def perform_create(self, serializer):
        # create partyroom need to connect a user as a owner
        serializer.save(owner=self.request.user)


class PartyRoomFilterView(generics.ListAPIView):
    queryset = PartyRoom.objects.all()
    authentication_classes = ()
    permission_classes = (SafelistPermission,)  
    serializer_class = PartyRoomSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PartyRoomFilter
    pagination_class = PageNumberPagination


class PartyRoomUIdDetail(generics.RetrieveAPIView):
    # Search by partyroom uid
    queryset = PartyRoom.objects.all()
    authentication_classes = ()
    permission_classes = (SafelistPermission,)
    serializer_class = PartyRoomDetailSerializer
    lookup_field = 'uid'


class PartyRoomImageCoverView(GenericViewSet):
    queryset = PartyRoom.objects.all()
    authentication_classes = ()
    permission_classes = (SafelistPermission,)
    serializer_class = PartyRoomImageGetSerializer
    
    @action(methods=['post'], detail=False, url_name='get_image_cover')
    def image_cover(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
                
        partyroom = PartyRoom.objects.get(uid=serializer.validated_data.get('uid'))
        read_serializer = self.get_serializer(partyroom)
        
        return Response(read_serializer.data, status=status.HTTP_200_OK)
    