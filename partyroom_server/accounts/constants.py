from error_code_list import *


ERROR_CODES = {
    'username': {
        'unique': USER_NAME_EXIST_ERROR_CODE
    },
    'phone_number': {
        'unique': PHONE_NUM_EXIST_ERROR_CODE,
        'invalid_phone_number': PHONE_NUM_INVALID_ERROR_CODE
    },
    'email': {
        'invalid': EMAIL_INVALID_ERROR_CODE
    },
    'favourite': {
        'not_a_dict': FAVOURITE_NOT_JSON_ERROR_CODE
    }
}
