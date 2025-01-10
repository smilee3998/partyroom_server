import json

from accounts.models import CustomUser
from django.urls import reverse
from error_code_list import *
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import PartyRoom
from .serializers import PartyRoomSerializer

small_room_1_data = {"name": "small_room_1",
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
                },
                'imageCover': ''
                }
small_room_2_data = {"name": "small_room_2",
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
medium_room_1_data = {"name": "medium_room_1",
                "ratingStars": 8,
                "minNumUsers": 10,
                "maxNumUsers": 20,
                "area": "NT",
                "district": "TM",
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
medium_room_2_data = {"name": "medium_room_2",
                "ratingStars": 2,
                "minNumUsers": 10,
                "maxNumUsers": 30,
                "area": "NT",
                "district": "TW",
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
big_room_1_data = {"name": "big_room_1",
                "ratingStars": 5,
                "minNumUsers": 50,
                "maxNumUsers": 100,
                "area": "HKI",
                "district": "I",
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
big_room_2_data = {"name": "big_room_2",
                "ratingStars": 4,
                "minNumUsers": 40,
                "maxNumUsers": 80,
                "area": "KWN",
                "district": "WTS",
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
invalid_room_raw_data = {"name": "invalid_room",
                "ratingStars": 4,
                "minNumUsers": 40,
                "maxNumUsers": 80,
                "area": "KWN",
                "district": "WTS",
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



class PartyRoomCreateTests(APITestCase):
    create_url = reverse('create_partyroom')
    data = small_room_1_data

    def setUp(self):
        self.user = CustomUser.objects.create(username='roomer',
                                              password='some_password',
                                              phone_number='+85291234511',
                                              email='user2@example.com',
                                              is_roomer=True)
        self.token = Token.objects.create(user=self.user)
        self.api_auth()
         
    def api_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
            
    def test_create_partyroom_authenticated(self):
        response = self.client.post(self.create_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_create_partyroom_invalid_rating_stars(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['ratingStars'] = 11
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test max of ratingStars is 10
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [RATING_STARS_MAX_ERROR_CODE]})
        
        invalid_data['ratingStars'] = -1
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test min of ratingStars is 0
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [RATING_STARS_MIN_ERROR_CODE]})
        
    def test_create_partyroom_invalid_min_users(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['minNumUsers'] = 1000
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test max of minNumUser is 999
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [MIN_NUM_USERS_MAX_ERROR_CODE]})
        
        invalid_data['minNumUsers'] = 0
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test min of minNumUser is 1
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [MIN_NUM_USERS_MIN_ERROR_CODE]})
    
    def test_create_partyroom_invalid_max_users(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['maxNumUsers'] = 1000
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test max of maxNumUsers is 999
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [MAX_NUM_USERS_MAX_ERROR_CODE]})
        
        invalid_data['maxNumUsers'] = 0
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test min of maxNumUsers is 1, also this will raise error that max < min users
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [MIN_NUM_GTE_MAX_NUM_USERS_ERROR_CODE, MAX_NUM_USERS_MIN_ERROR_CODE]})
    
    def test_create_partyroom_min_greater_than_max(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['minNumUsers'] = 10
        invalid_data['maxNumUsers'] = 5
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test max of maxNumUsers is 999
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [MIN_NUM_GTE_MAX_NUM_USERS_ERROR_CODE]})
    
    def test_create_partyroom_invalid_district_choice(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['district'] = 10
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test district should be within the choices
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [DISTRICT_INVALID_CHOICE_ERROR_CODE]})
        
        invalid_data['district'] = 'abc'
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test district should be within the choices
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [DISTRICT_INVALID_CHOICE_ERROR_CODE]})

    def test_create_partyroom_invalid_area_choice(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['area'] = 10
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test area should be within the choices
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [AREA_INVALID_CHOICE_ERROR_CODE]})
        
        invalid_data['area'] = 'abc'
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test area should be within the choices
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [AREA_INVALID_CHOICE_ERROR_CODE]})

    def test_create_partyroom_invalid_rule_list(self):
        invalid_data = invalid_room_raw_data.copy()
        invalid_data['ruleList'] = 'abc'
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test area should be list
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [RULE_LIST_NOT_A_LIST_ERROR_CODE]})
        
        invalid_data['ruleList'] = {'abc': 'asd'}
        response = self.client.post(self.create_url, invalid_data, format='json')
        # test area should be list
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error_code_list': [RULE_LIST_NOT_A_LIST_ERROR_CODE]})
    

    
        
class PartyRoomUnauthorizedTest(APITestCase):
    create_url = reverse('create_partyroom')
    data = small_room_1_data
    
    def test_create_partyroom_unauthenticated(self):
        response = self.client.post(self.create_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    
          
    def test_non_roomer_create_partyroom(self):
        non_roomer_user = self.user = CustomUser.objects.create(username='non_roomer',
                                                                password='some_password',
                                                                phone_number='+85291234521',
                                                                email='user2@example.com',
                                                                is_roomer=False)
        self.token = Token.objects.create(user=non_roomer_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(self.create_url, big_room_1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
