import time

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Post, User, UserMetaData
from core.utils import get_refresh_and_access_tokens


def get_user(data: dict) -> User:
    try:
        user = User.objects.get(email=data.get("email"))
    except User.DoesNotExist:
        user = User.objects.create_user(**data)
    return user


def get_access(data: dict) -> str:
    user = get_user(data)
    _, access_token = get_refresh_and_access_tokens(user=user)
    return access_token


class AuthTestCase(APITestCase):
    def test_success_signup(self):
        data = {"email": "signup@tests.com", "password": "signup"}
        url = reverse("auth-signup")

        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.headers.get("set-auth-token"))
        self.assertIsNotNone(response.headers.get("set-auth-refresh-token"))

        created_user = response.data
        self.assertIsNotNone(created_user["id"])
        self.assertEqual(created_user["email"], data["email"])

    def test_user_meta_data(self):  # TODO investigate failing test
        data = {"email": "meta_data@tests.com", "password": "meta_data"}
        url = reverse("auth-signup")

        self.client.post(path=url, data=data, format="json")
        time.sleep(5)

        user = User.objects.get_by_natural_key(data["email"])
        user_meta_data = UserMetaData.objects.get(user=user)
        self.assertIsNotNone(user_meta_data.geo_data)
        self.assertIsNotNone(user_meta_data.public_holidays)

    def test_fail_signup(self):
        url = reverse("auth-signup")

        response = self.client.post(path=url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["email"])
        self.assertIsNotNone(errors["password"])

        response = self.client.post(
            path=url, data={"password": "signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["email"])

        response = self.client.post(
            path=url, data={"email": "signup@tests.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["password"])

    def test_success_login(self):
        data = {"email": "login@tests.com", "password": "login"}
        user = get_user(data)

        url = reverse("auth-login")
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.headers.get("set-auth-token"))
        self.assertIsNotNone(response.headers.get("set-auth-refresh-token"))

        logged_in_user = response.data
        self.assertEqual(logged_in_user["id"], user.pk)
        self.assertEqual(logged_in_user["email"], user.email)
        self.assertEqual(logged_in_user["email_verified"], user.email_verified)

    def test_fail_login(self):
        url = reverse("auth-login")

        response = self.client.post(path=url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["email"])
        self.assertIsNotNone(errors["password"])

        response = self.client.post(
            path=url, data={"password": "signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["email"])

        response = self.client.post(
            path=url, data={"email": "signup@tests.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data
        self.assertIsNotNone(errors["password"])


class UserTestCase(APITestCase):
    user_data = {"email": "me@tests.com", "password": "me"}

    def test_success_get_me(self):
        user = get_user(self.user_data)
        access_token = get_access(self.user_data)
        url = reverse("user-me")
        response = self.client.get(
            path=url, headers={"Authorization": f"Bearer {access_token}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        me = dict(response.data)
        self.assertEqual(me["id"], user.pk)

        self.assertTrue(
            set(me.keys()).issubset(
                {
                    "email",
                    "first_name",
                    "email_verified",
                    "last_name",
                    "meta_data",
                    "id",
                }
            )
        )

    def test_fail_get_me(self):
        url = reverse("user-me")
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = get_user(self.user_data)
        refresh_token, _ = get_refresh_and_access_tokens(user=user)

        response = self.client.get(
            path=url, headers={"Authorization": f"Bearer {refresh_token}"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user(self):
        user = get_user(self.user_data)
        _, access_token = get_refresh_and_access_tokens(user=user)
        update = {"first_name": "John", "last_name": "Doe"}

        self.assertNotEqual(user.first_name, update["first_name"])
        self.assertNotEqual(user.last_name, update["last_name"])

        url = reverse("user-detail", kwargs={"pk": user.pk})

        response = self.client.patch(
            path=url, data=update, headers={"Authorization": f"Bearer {access_token}"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = get_user(self.user_data)
        updated_user = response.data

        # Verify modified fields
        self.assertEqual(updated_user["first_name"], update["first_name"])
        self.assertEqual(updated_user["last_name"], update["last_name"])

        # Verify unmodified fields
        self.assertEqual(updated_user["id"], user.pk)
        self.assertEqual(updated_user["email"], user.email)
        self.assertEqual(updated_user["email_verified"], user.email_verified)

        # Verify db changes
        user = get_user(self.user_data)
        self.assertEqual(user.first_name, update["first_name"])
        self.assertEqual(user.last_name, update["last_name"])

    def test_user_permissions(self):
        authorized_user = get_user({"email": "authorized@test.com"})
        unauthorized_user_token = get_access({"email": "unauthorized@test.com"})

        url = reverse("user-detail", kwargs={"pk": authorized_user.pk})
        response = self.client.patch(
            path=url,
            data={},
            headers={"Authorization": f"Bearer {unauthorized_user_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_protected_endpoints_authorization(self):
        url = reverse("user-me")
        me_response = self.client.get(path=url)
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("user-detail", kwargs={"pk": 1})
        update_response = self.client.patch(path=url, data={})
        self.assertEqual(update_response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user({"email": "me@tests.com", "password": "me"})
        _, cls.access_token = get_refresh_and_access_tokens(user=user)
        cls.user = user

    def test_create_post(self):
        url = reverse("post-list")
        post_data = {"message": "post-message"}
        response = self.client.post(
            path=url,
            data=post_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        response_data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response_data["message"], post_data["message"])
        self.assertEqual(response_data["likes"], [])
        self.assertEqual(response_data["author"]["id"], self.user.pk)
        self.assertIsNotNone(response_data["created_at"])
        self.assertIsNotNone(response_data["updated_at"])

    def test_get_post(self):
        post_data = {"message": "get-message", "author": self.user}
        post = Post.objects.create(**post_data)

        url = reverse("post-detail", kwargs={"pk": post.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data

        self.assertTrue(isinstance(response_data, dict))
        self.assertEqual(post.pk, response_data["id"])

    def test_get_posts(self):
        posts = [{"message": "first-post"}, {"message": "second-post"}]
        for post in posts:
            Post.objects.create(**{**post, **{"author": self.user}})

        url = reverse("post-list")

        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        self.assertTrue(isinstance(response_data, list))
        self.assertTrue(len(response_data) != 0)

    def test_like_post(self):
        post = {"message": "like-post", "author": self.user}
        post = Post.objects.create(**post)
        self.assertEqual(len(post.likes.all()), 0)

        url = reverse("post-like")

        response = self.client.get(
            path=f"{url}?id={post.pk}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        self.assertEqual(len(response_data["likes"]), 1)

    def test_unlike_post(self):
        post = {"message": "unlike-post", "author": self.user}
        post = Post.objects.create(**post)
        post.likes.set([self.user])
        self.assertEqual(len(post.likes.all()), 1)

        url = reverse("post-unlike")

        response = self.client.get(
            path=f"{url}?id={post.pk}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        self.assertEqual(len(response_data["likes"]), 0)

    def test_update_post(self):
        post_data = {"message": "old-message", "author": self.user}
        post = Post.objects.create(**post_data)
        self.assertEqual(post.message, post_data["message"])

        url = reverse("post-detail", kwargs={"pk": post.pk})

        update = {"message": "new-message"}

        response = self.client.patch(
            path=url,
            data=update,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data

        # Verify modified fields
        self.assertEqual(response_data["message"], update["message"])
        self.assertGreater(
            response_data["updated_at"],
            post.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )

        # Verify unmodified fields
        self.assertEqual(
            response_data["created_at"],
            post.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(response_data["deleted_at"], None)
        self.assertEqual(response_data["is_deleted"], post.is_deleted)
        self.assertEqual(len(response_data["likes"]), len(post.likes.all()))
        self.assertEqual(response_data["author"]["id"], self.user.pk)

    def test_delete_post(self):
        post_data = {"message": "delete-message", "author": self.user}
        post = Post.objects.create(**post_data)

        url = reverse("post-detail", kwargs={"pk": post.pk})

        response = self.client.delete(
            path=url, headers={"Authorization": f"Bearer {self.access_token}"}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(id=post.pk, is_deleted=False)

        post = Post.objects.get(id=post.pk)
        self.assertIsNotNone(post.deleted_at)

    def test_post_update_permissions(self):
        author = get_user({"email": "author@test.com"})
        post = Post.objects.create(**{"message": "auth-message", "author": author})
        unauthorized_user_token = get_access({"email": "unauthorized_user@test.com"})

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = self.client.patch(
            path=url,
            data={},
            headers={"Authorization": f"Bearer {unauthorized_user_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_delete_permissions(self):
        author = get_user({"email": "author@test.com"})
        post = Post.objects.create(**{"message": "auth-message", "author": author})
        unauthorized_user_token = get_access({"email": "unauthorized_user@test.com"})

        url = reverse("post-detail", kwargs={"pk": post.pk})

        response = self.client.delete(
            path=url, headers={"Authorization": f"Bearer {unauthorized_user_token}"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_protected_endpoints_authorization(self):
        url = reverse("post-detail", kwargs={"pk": 1})

        delete_response = self.client.delete(path=url)
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)

        patch_response = self.client.patch(
            path=url,
            data={},
        )
        self.assertEqual(patch_response.status_code, status.HTTP_401_UNAUTHORIZED)
