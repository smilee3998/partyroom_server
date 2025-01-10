from logging import getLogger

from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from error_code_list import *
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from utils.permissions import *

from .filters import BookingUnavailableFilter
from .models import Booking
from .serializers import (AvailableBookingListSerializer,
                          BookingCancelSerializer, BookingDetailSerializer,
                          BookingListSerializer, BookingReserveSerializer)

logger = getLogger(__name__)

class BookingViewSet(GenericViewSet):
    queryset = Booking.objects.all()
    permission_classes = (IsAuthenticated, SafelistPermission, IsVerifiedUser,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookingUnavailableFilter


    def get_serializer_class(self):
        if self.action == 'reserve':
            # TODO can only reserve > now
            return BookingReserveSerializer
        elif self.action =='check_time':
            return AvailableBookingListSerializer
    
    @extend_schema(responses=AvailableBookingListSerializer(many=True))    
    @action(methods=['get'], detail=False, url_name='booking_check')
    def check_time(self, request, *args, **kwargs):
        if request.GET.get('booking_date') is None or request.GET.get('partyroom__uid') is None:
            # both parameters are required
            return Response({'error_code_list': [BOOKING_CHECK_TIME_PARAMETER_MISSING_ERROR]},
                            status=status.HTTP_400_BAD_REQUEST)
             
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)        

    @action(['post'], detail=False, url_name='booking_reserve')
    def reserve(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = (IsAuthenticated, SafelistPermission,IsBookingOwnerOrStaff, IsVerifiedUser)
    lookup_field = 'uid'

           
    def get(self, request, *args, **kwargs):
        # override the function for customizing the response 
        try:
            return self.retrieve(request, *args, **kwargs)
        except Http404:
            return Response({'error_code_list': [BOOKING_UID_DOES_NOT_EXIST_ERROR]},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e   
    

class MyBookingListView(ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = (IsAuthenticated, SafelistPermission, IsVerifiedUser, )
    
    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(user=user)
