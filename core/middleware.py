from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import AuthenticationMiddleware
from user.services import get_jwt_user


class JWTAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_jwt_user(request))
