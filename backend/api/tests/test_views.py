from django.utils import timezone

from api.models import Tier

from .test_setup import TestSetUp


class TestViews(TestSetUp):
    def test_user_can_login_with_correct_credentials(self):
        def helper(user):
            res = self.helper_get_jwt(user)
            self.assertEqual(res.status_code, 200)
            self.assertIsNotNone(res.data["refresh"])
            self.assertIsNotNone(res.data["access"])

        helper(self.user_tier_basic)
        helper(self.user_tier_enterprise)
        helper(self.user_tier_basic)

    def test_user_cannot_login_with_wrong_credentials(self):
        def helper(user):
            user = self.helper_mock_password(user, f"!{self.mocked_password}")
            res = self.helper_get_jwt(user)
            self.assertEqual(res.status_code, 401)
            self.assertIsNone(res.data.get("refresh"))
            self.assertIsNone(res.data.get("access"))

        helper(self.user_tier_basic)
        helper(self.user_tier_enterprise)
        helper(self.user_tier_basic)

    def test_unauthorized_user_cannot_upload(self):
        res = self.helper_upload_image(self.valid_image)

        self.assertEqual(res.status_code, 401)

    def test_unauthorized_user_cannot_list_own_links(self):
        res = self.helper_list_links()
        self.assertEqual(res.status_code, 401)

    def test_authorized_user_can_list_own_links(self):
        def helper(user):
            res = self.helper_list_links(user)
            self.assertEqual(res.status_code, 200)

            helper(self.user_tier_basic)
            helper(self.user_tier_premium)
            helper(self.user_tier_enterprise)

    def test_cannot_upload_image_with_wrong_extension(self):
        def helper(user, filename):
            res = self.helper_upload_image(filename, user)
            self.assertEqual(res.status_code, 400)

        for image in self.upload_invalid_images:
            helper(self.user_tier_enterprise, image)

    def test_can_upload_image_with_valid_extension(self):
        def helper(user, filename):
            res = self.helper_upload_image(filename, user)
            self.assertEqual(res.status_code, 201)

        for image in self.upload_valid_images:
            helper(self.user_tier_enterprise, image)

    def test_user_after_upload_get_correct_number_of_links_for_tier(self):
        def helper(user, links_number_should_be):
            res = self.helper_upload_image(self.valid_image, user)
            links_number = len(res.data.get("links", None))
            self.assertEqual(links_number, links_number_should_be)

        helper(self.user_tier_basic, 1)
        helper(self.user_tier_premium, 3)
        helper(self.user_tier_enterprise, 3)

    def test_user_with_no_priv_cannot_fetch_expiring_link(self):
        def helper(user, can_fetch_expire_should_be):
            valid_exp_second = 1_000
            can_fetch_expire = self.helper_get_expiring_link(user, valid_exp_second)
            self.assertEqual(can_fetch_expire, can_fetch_expire_should_be)

        helper(self.user_tier_basic, None)
        helper(self.user_tier_premium, None)

    def test_user_cannot_fetch_expiring_link_passing_incorrect_time(self):
        def helper(valid_exp_second):
            user_with_priv = self.user_tier_enterprise
            can_fetch_expire = self.helper_get_expiring_link(
                user_with_priv, valid_exp_second
            )
            self.assertEqual(can_fetch_expire, None)

        helper(299)
        helper(30_001)

        helper("299")
        helper("30_001")

        helper(299.9)
        helper(15_000.9)
        helper(30_000.9)

        helper("299.9")
        helper("15_000.9")
        helper("30_000.9")

        helper("299,9")
        helper("15_000,9")
        helper("30_000,9")

        helper("Hello, world")

    def test_user_cann_fetch_expiring_link_passing_correct_time(self):
        def helper(valid_exp_second):
            user_with_priv = self.user_tier_enterprise
            can_fetch_expire = self.helper_get_expiring_link(
                user_with_priv, valid_exp_second
            )
            self.assertIsNotNone(can_fetch_expire)

        helper(300)
        helper(301)
        helper(29_999)
        helper(30_000)

    def test_after_upload_user_get_correct_image_thumbnail_hitting_returned_links(self):
        def helper(user):
            res = self.helper_upload_image(self.valid_image, user)
            links = res.data.get("links", None)
            for link in links:
                url = link.get("url", None)
                height = link.get("resize", None)
                res_media = self.client.get(url)
                self.helper_compare_uploaded_image_with_image_got_by_url(
                    self.valid_image, res_media, compare_height_value=height
                )

        helper(self.user_tier_basic)
        helper(self.user_tier_premium)
        helper(self.user_tier_enterprise)

    def test_user_cannot_get_image_when_link_expired(self):
        def past_date(secs):
            now = timezone.now()
            return now + timezone.timedelta(seconds=secs)

        self.helper_mock_expiring_link_and_hit_endpoint(
            past_date(-1), response_status_code_should_be=404
        )

        self.helper_mock_expiring_link_and_hit_endpoint(
            past_date(0), response_status_code_should_be=404
        )

    def test_user_can_get_image_when_link_not_expired(self):
        def past_date(secs):
            now = timezone.now()
            return now + timezone.timedelta(seconds=secs)

        self.helper_mock_expiring_link_and_hit_endpoint(
            past_date(1), response_status_code_should_be=200
        )

    def test_user_with_custom_tier_get_correct_links(self):
        thumbnail_size = 468
        thumbnail_size_bigger = 789
        custom_tier = Tier(
            name=f"{self.faker.name()} Tier",
            thumbnail_size=thumbnail_size,
            thumbnail_size_bigger=thumbnail_size_bigger,
            presence_of_link_to_og_file=True,
            ability_to_create_exp_link=True,
        )
        custom_tier.save()
        user = self.user_tier_basic
        user.tier = custom_tier
        user.save()

        res = self.helper_upload_image(self.valid_image, user, 15_000)
        links = res.data.get("links", None)

        self.assertEqual(links[0].get("resize", None), thumbnail_size)
        self.assertEqual(links[1].get("resize", None), thumbnail_size_bigger)
        self.assertEqual(links[2].get("resize", None), None)
        self.assertIsNotNone(links[3].get("expires", None))
