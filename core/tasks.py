from core.models import User, UserMetaData
from core.utils import AbstractAPI
from social_network_backend.celery import app


@app.task
def save_user_meta_data(ip_address: str, username: str):
    user = User.objects.get_by_natural_key(username)
    geo_data = AbstractAPI.get_geo_data(ip_address)
    meta_data = UserMetaData(user=user, geo_data=geo_data)
    meta_data.save()

    public_holidays = AbstractAPI.get_public_holidays(
        country_code=geo_data.get("country_code", ""), date=user.created_at
    )
    meta_data.public_holidays = public_holidays
    meta_data.save()
