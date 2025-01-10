from datetime import datetime, timedelta, timezone

from accounts.models import CustomUser
from django.urls import reverse
from error_code_list import *
from main.models import PartyRoom
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


room_1_data = {"name": "small_room_1",
                "ratingStars": 10,
                "minNumUsers": 1,
                "maxNumUsers": 5,
                "area": "KWN",
                "district": "CW",
                "fullAddress": "string",
                "shortDesp": "string",
                "description": "string",
                "ruleList": [
                ],
                "venueFaciList": [
                ],
                "entertainFaciList": [
                ],
                "gameList": {
                },
                "boardgameList": [
                ],
                "addtionalServiceList": [
                    "string"
                ],
                "chargeList": {
                },
                "bookingMethodList": [
                    "string"
                ],
                "transportList": {
                }
                }

room_2_data = {"name": "small_room_2",
                "ratingStars": 9,
                "minNumUsers": 1,
                "maxNumUsers": 5,
                "area": "NT",
                "district": "YL",
                "fullAddress": "string",
                "shortDesp": "string",
                "description": "string",
                "ruleList": [
                ],
                "venueFaciList": [
                ],
                "entertainFaciList": [
                ],
                "gameList": {
                },
                "boardgameList": [
                ],
                "addtionalServiceList": [
                    "string"
                ],
                "chargeList": {
                },
                "bookingMethodList": [
                    "string"
                ],
                "transportList": {
                },
                'imageCover': ''
                }

utc8 = timezone(timedelta(hours=8))

now = datetime.now(utc8)

booking_data_1 = {
    # "partyroom": "str",
    "start_time": now.isoformat(),
    "end_time": (now + timedelta(hours=1)).isoformat(),
    "num_users": 2,
    "unit_price": 10,
    "total_price": 10
}

class BookingCreateTests(APITestCase):
    reserve_url = reverse('booking-booking_reserve')
    
    def setUp(self):
        self.roomer = CustomUser.objects.create(username='roomer',
                                        password='some_password',
                                        phone_number='+85291234511',
                                        email='user1@example.com',
                                        is_roomer=True)
        self.booking_user = CustomUser.objects.create(username='booking_user',
                                              password='some_password',
                                              phone_number='+85291234512',
                                              email='user2@example.com',
                                              is_roomer=False)
        self.room1 = PartyRoom.objects.create(**room_1_data, owner=self.roomer)
        self.room2 = PartyRoom.objects.create(**room_2_data, owner=self.roomer)
        self.token = Token.objects.create(user=self.booking_user)
        self.api_auth()    
        
    def api_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        
    def test_reserve_room_authenticated(self):
        booking_data_1['partyroom'] = self.room1.uid
        response = self.client.post(self.reserve_url, booking_data_1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = booking_data_1
        response_data['partyroom'] = self.room1.name

        self.assertEqual(response.data, response_data)
        
      
        
        
        