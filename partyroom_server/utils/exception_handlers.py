from typing import List
from rest_framework.views import exception_handler
from logging import getLogger


from error_code_list import *


logger = getLogger(__name__)

def custom_exception_handler(exc, context):
    """[summary]

    Args:
        exc: exception specific information
        context: other information such as which view is throwing the exception
    """    
    handlers = {
        'ValidationError': _handle_validation_error,
    }
    response = exception_handler(exc, context)
    exception_class = exc.__class__.__name__
    
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response
    
def get_error_code(field, detail, error_code_list: List):
    if detail[:5] == 'ERROR':
        # recognized error
        error_code_list.append(detail[:])
    # Below is hard code to handle known error that don't know how to process
    elif field[0] == 'booking_date' and detail.code == 'invalid':
        # invalid type of date for BookingUnavailableFilter in booking
        # TODO no hard code
        error_code_list.append(BOOKING_DATE_INVALID_ERROR)
    elif field[0] == 'non_field_errors' and detail.code == 'authorization':
        # TODO no hard code
        error_code_list.append(CREDENTIALS_INVALID_ERRORS)
    else:
        logger.warning(f'Unknown error. {detail=}')  
        
def _handle_validation_error(exc, context, response):
    error_code_list = []
    for field in exc.detail.items():
        if isinstance(field[1], dict):
            # nested error
            for value in field[1].values():
                for detail in value:
                    logger.debug(f'{exc=} {context=}')
                    get_error_code(field, detail, error_code_list)

        elif isinstance(field[1], list):            
            for detail in field[1]:  # list of ErrorDetails
                logger.debug(f'{context=} {field=}  {detail[:]=}')
                get_error_code(field, detail, error_code_list)
                
        else:
            logger.warning(f'Unknown field type {type(field[1])}')
              
    response.data = {
        'error_code_list': error_code_list
    }
    return response