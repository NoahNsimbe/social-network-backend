import string
import random
from datetime import datetime

import jwt
import requests
from jwt import InvalidSignatureError, DecodeError
from requests.adapters import HTTPAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from urllib3 import Retry

from core.models import User
from social_network_backend.settings import SECRET_KEY, ABSTRACT_API_KEY


def get_refresh_and_access_tokens(user: User):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def decode_token(token: str) -> dict:
    try:
        token_content = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return token_content
    except (InvalidSignatureError, DecodeError):
        return {}


def n_length_alphanumeric(length, upper=True):
    value = ""
    for i in range(length):
        choices = string.ascii_letters if i % 2 == 1 else string.digits
        if upper is True:
            value += "".join(random.choices(choices, k=1)).upper()
        else:
            value += "".join(random.choices(choices, k=1)).lower()
    return value


def generate_post_slug(post, tries=0):
    slug = post.message.strip().replace(" ", "-").lower()
    if tries == 0:
        post.slug = slug
    elif tries > 4:
        post.slug = f"{post.pk}-{slug}-{n_length_alphanumeric(5, False)}"
    else:
        post.slug = f"{slug}-{n_length_alphanumeric(5, False)}"

    try:
        post.save(update_fields=["slug"])
    except Exception:
        if tries < 5:
            generate_post_slug(post, tries + 1)


class AbstractAPI:
    retry_strategy = Retry(
        total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
    )

    @staticmethod
    def get_geo_data(ip_address: str) -> dict:
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=AbstractAPI.retry_strategy))
        try:
            response = session.get(
                url="https://ipgeolocation.abstractapi.com/v1",
                params={"api_key": ABSTRACT_API_KEY, "ip_address": ip_address},
            )
            if response.status_code == 200:
                return response.json()
        except Exception as ex:
            print(ex)
        return {}

    @staticmethod
    def get_public_holidays(country_code: str, date: datetime) -> list:
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=AbstractAPI.retry_strategy))
        try:
            response = session.get(
                url="https://holidays.abstractapi.com/v1",
                params={
                    "api_key": ABSTRACT_API_KEY,
                    "country": country_code,
                    "year": date.year,
                    "month": date.month,
                    "day": date.day,
                },
            )
            if response.status_code == 200:
                return response.json()
        except Exception as ex:
            print(ex)
        return []
