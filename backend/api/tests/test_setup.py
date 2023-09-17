import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from api.models import Tier, User


class TestSetUp(APITestCase):
    fixtures = ['default_tiers.json', 'test_users.json']

    def helper_mock_password(self, user, mocked_password):
        user.set_password(mocked_password)
        user.save()
        return user

    def helper_get_jwt(self, user):
        data = {
            'username': user.username,
            'password': self.mocked_password
        }
        res = self.client.post(self.token_api, data=data, format='json')
        return res

    def helper_upload_image(self, img_path, user_authorized=None, exp_seconds=None):
        if user_authorized is not None:
            token = self.helper_get_jwt(
                user_authorized).data.get('access', None)
            self.client.credentials(
                HTTP_AUTHORIZATION=f'{self.key_auth_header_prefix}{token}')

        api_url = self.images_api
        api_url += f'{self.images_api_exp_seconds_query_key}{exp_seconds}' if exp_seconds is not None else ''

        file_path = os.path.join(
            settings.BASE_DIR, 'api', 'tests', 'data', img_path)

        with open(file_path, 'rb') as fp:
            data = SimpleUploadedFile(
                fp.name, fp.read())
            res = self.client.post(api_url, {self.key_file_upload: data})
            return res

    def helper_list_links(self, user_authorized=None):
        if user_authorized is not None:
            token = self.helper_get_jwt(
                user_authorized).data.get('access', None)
            self.client.credentials(
                HTTP_AUTHORIZATION=f'{self.key_auth_header_prefix}{token}')

        res = self.client.get(self.images_api)
        return res

    def helper_get_expiring_link(self, user, exp_seconds):
        res = self.helper_upload_image(
            self.valid_image, user, exp_seconds=exp_seconds)

        if res.status_code == 400:
            return False
        contains_key_expires = any(
            'expires' in exp for exp in res.data.get('links', None))
        return contains_key_expires

    def setUp(self):
        self.faker = Faker()

        self.key_auth_header_prefix = 'Bearer '
        self.key_file_upload = settings.MEDIA_UPLOAD_KEY

        # self.mediafiles_api = reverse('mediafiles_api')
        self.images_api = reverse('images_api')
        self.token_api = reverse('token_obtain_pair')
        self.images_api_exp_seconds_query_key = '?exp='

        self.upload_valid_images = ['img.jpg', 'img.png']
        self.upload_invalid_images = [
            'img', 'img.', 'img.gif', 'img.img.img', 'img.psd', 'img.tif', 'img.webp']
        self.valid_image = self.upload_valid_images[0]
        self.invalid_image = self.upload_invalid_images[0]

        self.tier_basic = Tier.objects.get(name='Basic')
        self.tier_premium = Tier.objects.get(name='Premium')
        self.tier_enterprise = Tier.objects.get(name='Enterprise')

        self.mocked_password = self.faker.password()

        self.user_tier_basic = self.helper_mock_password(
            User.objects.get(tier=self.tier_basic), self.mocked_password)
        self.user_tier_premium = self.helper_mock_password(
            User.objects.get(tier=self.tier_premium), self.mocked_password)
        self.user_tier_enterprise = self.helper_mock_password(
            User.objects.get(tier=self.tier_enterprise), self.mocked_password)

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
