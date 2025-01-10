import json
from datetime import timedelta
from logging import getLogger

from django.urls import reverse
from error_code_list import *
from main.models import PartyRoom
from main.serializers import PartyRoomSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from utils.utils import now

from .models import OTP, CustomUser
from .serializers import CustomUserSerializer

logger = getLogger('account_test')

class RoomerAccountTests(APITestCase):
    def test_create_roomer_account(self):
        url = reverse('user_register')
        data = {'username': 'roomer_tester',
                'password': 'password123',
                'phone_number': '+85291234567',
                "email": "user@example.com",
                'is_roomer': True,
                'favourite': {}
                }

        response = self.client.post(url, data, format='json')
        # Check the user is successfully registered
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user_instance = CustomUser.objects.get(username='roomer_tester')
        user_serializer_data = CustomUserSerializer(instance=user_instance).data
        response_data = json.loads(response.content)

        # check the user's data is correct
        self.assertEqual(user_serializer_data, response_data)


class NormalAccountTests(APITestCase):
    def test_create_normal_user(self):
        url = reverse('user_register')
        data = {'username': 'normal_user_tester',
                'password': 'password123',
                'phone_number': '+85291234566',
                "email": "user2@example.com",
                'is_roomer': False,
                'favourite': {}
                }
        response = self.client.post(url, data, format='json')
        # check the user is successfully registered
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user_instance = CustomUser.objects.get(username='normal_user_tester')
        user_serializer_data = CustomUserSerializer(instance=user_instance).data
        # user_serializer_data['status'] = 'Success'
        response_data = json.loads(response.content)
        # check the user's data is correct        
        self.assertEqual(user_serializer_data, response_data)
        


class InvalidAccountCreateTests(APITestCase):
    url = reverse('user_register')
    
    def setUp(self):
        existing_user = CustomUser.objects.create(username='normal_user_tester2',
                                                  password='some_password',
                                                  phone_number='+85291234566',
                                                  email='user2@example.com',
                                                  is_roomer=False)
    
    def test_create_user_invalid_phone_number(self):            
        # check create user with invalid phone_number
        invalid_data = {'username': 'invalid_user_tester',
                        'password': 'password123',
                        'phone_number': '+852912345',
                        "email": "user2@example.com",
                        'is_roomer': False,
                        'favourite': {}
                        }
        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.data, {'error_code_list': [PHONE_NUM_INVALID_ERROR_CODE]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_same_phone_number(self):    
        # check create user with same phone number
        invalid_data = {'username': 'invalid_user_tester',
                        'password': 'password123',
                        'phone_number': '+85291234566',
                        "email": "user2@example.com",
                        'is_roomer': False,
                        'favourite': {}
                        }
        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.data, {'error_code_list': [PHONE_NUM_EXIST_ERROR_CODE]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_same_username(self):    
        # check create user with same username
        invalid_data = {'username': 'normal_user_tester2',
                        'password': 'password123',
                        'phone_number': '+85291234561',
                        "email": "user2@example.com",
                        'is_roomer': False,
                        'favourite': {}
                        }
        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.data, {'error_code_list': [USER_NAME_EXIST_ERROR_CODE]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
   
    def test_create_user_invalid_email(self):
        # check create user with invalid emailField
        invalid_data = {'username': 'invalid_user_tester',
                        'password': 'password123',
                        'phone_number': '+85291234561',
                        "email": "user2",
                        'is_roomer': False,
                        'favourite': {}
                        }
        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.data, {'error_code_list': [EMAIL_INVALID_ERROR_CODE]})

class UserFavoritesTests(APITestCase):
    def setUp(self):
        self.create_roomer_user()
        self.create_partyrooms()
        self.token = Token.objects.create(user=self.user)
        self.api_auth()
        self.url = reverse('user_favourite')


    def api_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
           
    def create_partyrooms(self):
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
        self.partyroom1 = PartyRoom.objects.create(owner=self.user, **small_room_1_data)
        self.partyroom2 = PartyRoom.objects.create(owner=self.user, **small_room_2_data)
            
    def create_roomer_user(self):
        data = {'username': 'roomer_tester3',
                'password': 'password123',
                'phone_number': '+85291234561',
                "email": "user@example.com",
                'is_roomer': True,
                }
        self.user = CustomUser.objects.create(**data)
         
    def test_user_favourite(self):
        data = {'favourites': [self.partyroom1.uid, self.partyroom2.uid]}
        # check adding favourite to user
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'Success'})
        
        # check getting favourite from user        
        serialized_partyroom1_data = PartyRoomSerializer(instance=self.partyroom1).data
        serialized_partyroom2_data = PartyRoomSerializer(instance=self.partyroom2).data
        response = self.client.get(self.url)
                                     
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'favourites': [serialized_partyroom1_data, serialized_partyroom2_data]})

        # check delete favourite from user
        data = {'favourites': [self.partyroom1.uid]}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.data, {'status': 'Success'})
        
        # check it is correctly deleted
        response = self.client.get(self.url)
        self.assertEqual(response.data, {'favourites': [serialized_partyroom2_data]})
    
    def test_user_favourite_error(self):
        data = {'favourites': [self.partyroom1.uid]}
        random_uid = 'ABCD'
        _ = self.client.put(self.url, data, format='json')

        # put non-exist partyroom uid to user's favorites  
        data = {'favourites': [random_uid]}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.data, {'error_code_list': [PARTY_ROOM_DOES_NOT_EXIST_ERROR]})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # delete exist partyroom uid but not in user's favorites 
        exist_uid = self.partyroom2.uid
        data = {'favourites': [exist_uid]}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.data, {'error_code_list': [PARTY_ROOM_UID_NOT_IN_USER_FAVOURITES_ERROR]})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPtests(APITestCase):
    data = {'username': 'some_user',
            'password': 'password123',
            'phone_number': '+85291234566',
            "email": "user3@example.com",
            'is_roomer': False,
        }
    requests_url = reverse('otp-requests_otp')
    verify_url = reverse('otp-verify_otp')
    
    def setUp(self):
        self.user = CustomUser.objects.create(**self.data)
        self.otp = OTP.objects.create(user=self.user, type='EV')
        self.token = Token.objects.create(user=self.user)
        self.api_auth()
        
    def api_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
                
    def test_requests_otp(self):
        # TODO test without actually send email?
        pass
    
    def test_wrong_otp(self):
        uid = self.otp.uid
        data = {'email': self.user.email, 'otp_code':'code', 'otp_uid': uid}
        
        response = self.client.post(self.verify_url, data=data, format='json')
        self.assertEqual(response.data, {'error_code_list': [OTP_INCORRECT_ERROR_CODE]})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_inexist_otp(self):
        code = self.otp.otp_code
        data = {'email':self.user.email, 'otp_code': code, 'otp_uid': '123'}
        
        response = self.client.post(self.verify_url, data=data, format='json')
        self.assertEqual(response.data, {'error_code_list': [OTP_INEXIST_ERROR_CODE]})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)    
        
    def test_expires_otp(self):
        delta = timedelta(hours=2)
        new_time = self.otp.expires_at - delta
        self.otp.expires_at = new_time
        self.otp.save()
        
        uid = self.otp.uid
        code = self.otp.otp_code
        data = {'email':self.user.email, 'otp_code':code, 'otp_uid': uid}
        
        response = self.client.post(self.verify_url, data=data, format='json')
        self.assertEqual(response.data, {'error_code_list': [OTP_EXPIRES_ERROR_CODE]})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

        
        
         
                        
    


