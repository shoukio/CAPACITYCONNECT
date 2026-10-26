import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Profile


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RegistrationTests(TestCase):
    def test_registration_creates_a_learner_and_signs_them_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newlearner",
                "first_name": "New",
                "last_name": "Learner",
                "email": "learner@example.com",
                "password1": "Safe-Password-139!",
                "password2": "Safe-Password-139!",
            },
        )

        user = get_user_model().objects.get(username="newlearner")
        self.assertRedirects(response, reverse("core:learner_dashboard"))
        self.assertEqual(user.profile.role, Profile.Role.LEARNER)
        self.assertTrue(user.groups.filter(name="Learner").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_registration_does_not_accept_a_role_from_the_form(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "trainerattempt",
                "email": "trainer@example.com",
                "role": Profile.Role.ADMINISTRATOR,
                "password1": "Safe-Password-139!",
                "password2": "Safe-Password-139!",
            },
        )

        user = get_user_model().objects.get(username="trainerattempt")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.profile.role, Profile.Role.LEARNER)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AccountFlowTests(TestCase):
    def test_regular_login_offers_separate_administrator_sign_in(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Use administrator sign in")
        self.assertContains(response, reverse("accounts:admin_login"))

    def test_administrator_login_accepts_admin_and_routes_to_admin_dashboard(self):
        administrator = get_user_model().objects.create_superuser(
            username="portaladmin",
            email="admin@example.com",
            password="Safe-Password-139!",
        )

        response = self.client.post(
            reverse("accounts:admin_login"),
            {"username": administrator.username, "password": "Safe-Password-139!"},
        )

        self.assertRedirects(response, reverse("core:administrator_dashboard"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            administrator.pk,
        )

    def test_administrator_login_rejects_learner_without_signing_them_in(self):
        learner = get_user_model().objects.create_user(
            username="learner",
            password="Safe-Password-139!",
        )

        response = self.client.post(
            reverse("accounts:admin_login"),
            {"username": learner.username, "password": "Safe-Password-139!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "do not belong to an administrator account")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_administrator_login_requires_staff_permission(self):
        staff_user = get_user_model().objects.create_user(
            username="nonstaff-admin-role",
            password="Safe-Password-139!",
            is_staff=False,
        )
        staff_user.profile.role = Profile.Role.ADMINISTRATOR
        staff_user.profile.save()

        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "username": staff_user.username,
                "password": "Safe-Password-139!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "do not belong to an administrator account")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_and_post_logout(self):
        user = get_user_model().objects.create_user(
            username="learner",
            password="Safe-Password-139!",
        )

        login_response = self.client.post(
            reverse("accounts:login"),
            {"username": user.username, "password": "Safe-Password-139!"},
        )
        logout_response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(login_response.status_code, 302)
        self.assertRedirects(logout_response, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_flows_load(self):
        user = get_user_model().objects.create_user(
            username="learner",
            email="learner@example.com",
            password="Safe-Password-139!",
        )

        self.assertEqual(
            self.client.get(reverse("accounts:password_reset")).status_code,
            200,
        )
        self.client.force_login(user)
        self.assertEqual(
            self.client.get(reverse("accounts:password_change")).status_code,
            200,
        )

    def test_password_reset_changes_password_using_email_link(self):
        user = get_user_model().objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="Original-safe-Password-184!",
        )

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.client.post(
                reverse("accounts:password_reset"),
                {"email": user.email},
            )

        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        reset_path = re.search(
            r"http://testserver(/accounts/password-reset/\S+)",
            mail.outbox[0].body,
        ).group(1)
        reset_response = self.client.get(reset_path, follow=True)

        self.assertEqual(reset_response.status_code, 200)
        self.assertContains(reset_response, "Choose a new password")
        confirm_path = reset_response.request["PATH_INFO"]
        response = self.client.post(
            confirm_path,
            {
                "new_password1": "New-safe-Password-184!",
                "new_password2": "New-safe-Password-184!",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_complete"),
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password("New-safe-Password-184!"))


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RoleAndDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="learner",
            password="Safe-Password-139!",
        )

    def test_guest_is_sent_to_login_before_dashboard(self):
        response = self.client.get(reverse("core:learner_dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('core:learner_dashboard')}",
        )

    def test_learner_can_open_only_learner_dashboard(self):
        self.client.force_login(self.user)

        learner_response = self.client.get(reverse("core:learner_dashboard"))
        trainer_response = self.client.get(reverse("core:trainer_dashboard"))
        administrator_response = self.client.get(
            reverse("core:administrator_dashboard")
        )

        self.assertEqual(learner_response.status_code, 200)
        self.assertContains(learner_response, "Your growth, at your pace.")
        self.assertEqual(trainer_response.status_code, 403)
        self.assertEqual(administrator_response.status_code, 403)

    def test_dashboard_dispatches_to_the_profile_role(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertRedirects(response, reverse("core:learner_dashboard"))

    def test_profile_and_role_group_must_both_allow_access(self):
        self.user.groups.remove(Group.objects.get(name="Learner"))
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:learner_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_profile_role_change_keeps_role_group_in_sync(self):
        extra_group = Group.objects.create(name="Extra permissions")
        self.user.groups.add(extra_group)
        self.user.profile.role = Profile.Role.TRAINER
        self.user.profile.save()

        self.assertTrue(self.user.groups.filter(name="Trainer").exists())
        self.assertFalse(self.user.groups.filter(name="Learner").exists())
        self.assertTrue(self.user.groups.filter(pk=extra_group.pk).exists())

    def test_superuser_gets_administrator_dashboard(self):
        administrator = get_user_model().objects.create_superuser(
            username="administrator",
            email="admin@example.com",
            password="Safe-Password-139!",
        )
        self.client.force_login(administrator)

        response = self.client.get(reverse("core:dashboard"))

        self.assertRedirects(response, reverse("core:administrator_dashboard"))
        self.assertEqual(
            self.client.get(reverse("core:administrator_dashboard")).status_code,
            200,
        )

    def test_existing_user_profile_role_redirects_to_correct_dashboard(self):
        self.user.profile.role = Profile.Role.TRAINER
        self.user.profile.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertRedirects(response, reverse("core:trainer_dashboard"))

    def test_public_course_routes_remain_available(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:course_list"))

        self.assertEqual(response.status_code, 200)

    def test_login_form_rejects_post_without_csrf_token(self):
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": "Safe-Password-139!"},
        )

        self.assertEqual(response.status_code, 403)