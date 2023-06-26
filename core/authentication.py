from datetime import datetime, timedelta

import pytz
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from core.utils import get_refresh_and_access_tokens


class AuthTokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            raw_token = request.headers["Authorization"].split(" ")[1]
        except (KeyError, IndexError):
            return response

        try:
            token = AccessToken(raw_token, True)
        except TokenError:
            return response

        try:
            current_time = (datetime.now() + timedelta(hours=6)).replace(
                tzinfo=pytz.UTC
            )
            token.check_exp(current_time=current_time)
        except TokenError:
            user = request.user
            refresh_token, access_token = get_refresh_and_access_tokens(user)
            response["set-auth-token"] = access_token
            response["set-auth-refresh-token"] = refresh_token

        return response
