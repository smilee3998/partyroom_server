from rest_framework.response import Response
from rest_framework import status
from error_code_list import *


ALLOWED_RESPONSE = Response(data={'allowed': True},
                           status=status.HTTP_200_OK)
ALL_QUOTA_USED_RESPONSE = Response(data={'status': 'Fail'},
                                   status=status.HTTP_400_BAD_REQUEST)
REVIEW_DETAIL_NOT_PROVIED_RESPONSE = Response(data={'status': 'Fail', 'error_code_list': [REVIEW_DETAIL_NOT_PROVIED_ERROR]},
                                              status=status.HTTP_400_BAD_REQUEST)