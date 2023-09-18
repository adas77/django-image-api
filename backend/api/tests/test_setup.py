import os
from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.response import FileResponse
from django.urls import reverse
from faker import Faker
from PIL import Image
from rest_framework.test import APITestCase

from api.models import Link, Tier, User


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

    def helper_get_test_images_path(self, filename):
        return os.path.join(
            settings.BASE_DIR, 'api', 'tests', 'data', filename)

    def helper_upload_image(self, img_path, user_authorized=None, exp_seconds=None):
        if user_authorized is not None:
            token = self.helper_get_jwt(
                user_authorized).data.get('access', None)
            self.client.credentials(
                HTTP_AUTHORIZATION=f'{self.key_auth_header_prefix}{token}')

        api_url = self.images_api
        api_url += f'{self.images_api_exp_seconds_query_key}{exp_seconds}' if exp_seconds is not None else ''

        file_path = self.helper_get_test_images_path(img_path)

        with open(file_path, 'rb') as fp:
            data = SimpleUploadedFile(
                fp.name, fp.read())
            res = self.client.post(api_url, {self.key_file_upload: data})
            return res

    def helper_compare_uploaded_image_with_image_got_by_url(self, image_name_before: str, image_response_after: FileResponse,
                                                            compare_height_value: int = None, compare_content_type=True, compare_width=False):
        with Image.open(self.helper_get_test_images_path(image_name_before)) as img:
            b_width, b_height = img.size
            b_content_type = img.format

        content_bytes = b''.join(image_response_after.streaming_content)
        with Image.open(BytesIO(content_bytes)) as img:
            a_width, a_height = img.size
            a_content_type = img.format

        if compare_height_value is None:
            self.assertEqual(b_height, a_height)
        else:
            self.assertEqual(compare_height_value, a_height)
        if compare_width:
            self.assertEqual(b_width, a_width)
        if compare_content_type:
            self.assertEqual(b_content_type, a_content_type)

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
            return None
        for exp in res.data.get('links', []):
            if 'expires' in exp:
                return exp['url']
        return None

    def helper_mock_expiring_link_and_hit_endpoint(self, mock_expire_date, response_status_code_should_be):
        url = self.helper_get_expiring_link(
            self.user_tier_enterprise, 15_000)
        url_image_id = url.split('/')[-1]
        Link.objects.filter(url=url_image_id).update(
            expires=mock_expire_date)
        res = self.client.get(url)
        self.assertEqual(res.status_code, response_status_code_should_be)

    def setUp(self):
        self.faker = Faker()

        self.key_auth_header_prefix = 'Bearer '
        self.key_file_upload = settings.MEDIA_UPLOAD_KEY

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
