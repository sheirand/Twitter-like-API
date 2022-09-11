from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import AuthenticationMiddleware
from user.services import JWTService


class JWTAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: JWTService.get_jwt_user(request))
