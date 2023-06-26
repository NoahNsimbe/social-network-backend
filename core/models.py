from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import JSONField
from django.utils import timezone


class ModelMetaData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()


class UserManager(BaseUserManager):
    def create_user(self, **other_fields):
        password = other_fields.pop("password", None)
        user = self.model(**other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **other_fields):
        other_fields["is_superuser"] = True
        return self.create_user(**other_fields)


def image_folder(_, filename):
    return "/".join(["images", filename])


class User(ModelMetaData, PermissionsMixin, AbstractBaseUser):
    USERNAME_FIELD = "email"
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=2048, null=True, blank=True)
    last_name = models.CharField(max_length=2048, null=True, blank=True)
    password = models.CharField(max_length=2048, null=False, blank=False)
    email_verified = models.BooleanField(default=False, blank=False, null=False)
    profile_picture = models.ImageField(upload_to=image_folder, blank=True, null=True)
    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return self.email


class UserMetaData(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="meta_data"
    )
    geo_data = JSONField(null=True, blank=True)
    public_holidays = JSONField(null=True, blank=True)


class Post(ModelMetaData):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    message = models.CharField(max_length=2048, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True, unique=True)
    likes = models.ManyToManyField(to=User, blank=True, related_name="likes")

    def __str__(self):
        return self.message or f"Post ID - {self.pk}"
