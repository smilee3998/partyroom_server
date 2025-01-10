from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import (
    OpenApiSerializerExtension, OpenApiSerializerFieldExtension, OpenApiViewExtension, OpenApiAuthenticationExtension
)
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_field, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# ref: https://drf-spectacular.readthedocs.io/en/latest/blueprints.html


class KnoxTokenScheme(OpenApiAuthenticationExtension):
    # ref: https://github.com/tfranzel/drf-spectacular/issues/264
    target_class = 'knox.auth.TokenAuthentication'
    name = 'knoxTokenAuth'

    def get_security_definition(self, auto_schema):        
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': _(
                'Token-based authentication with required prefix "%s"'
            ) % "Token"
        }
        
        
class AccountOTPViewVerifyFix(OpenApiViewExtension):
    target_class = 'accounts.views.AccountOTPView'
    
    def view_replacement(self):
        class Fixed(self.target_class):
            
         @extend_schema(responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT},
            examples=[
            OpenApiExample(
                'OTP verify 200 example',
                value={'status': 'Success'},
                response_only=True,
                status_codes=['200']),
            OpenApiExample(
                'OTP verify 400 example',
                value={'error_code_list': '[ERROR-XXXX]'},
                response_only=True,
                status_codes=['400']),
        ])
         def verify(self, request, *args, **kwargs):
             pass
        return Fixed
     