from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username="yuri", email="yuri@example.com", password="rahasia123", first_name="Yuri"
        )
        # Akun lama: username sama dengan email.
        User.objects.create_user(
            username="lama@example.com", email="lama@example.com", password="rahasia123"
        )

    def login(self, identifier):
        return self.client.post(
            "/api/token/", {"username": identifier, "password": "rahasia123"}, format="json"
        )

    def test_login_with_username_or_email(self):
        for identifier in ("yuri", "YURI", "yuri@example.com", " Yuri@Example.com "):
            response = self.login(identifier)
            self.assertEqual(response.status_code, 200, identifier)
            self.assertEqual(response.data["user"]["username"], "yuri")
            self.assertIn("access", response.data)

    def test_old_account_still_logs_in_with_email(self):
        self.assertEqual(self.login("lama@example.com").status_code, 200)

    def test_wrong_password_rejected(self):
        response = self.client.post(
            "/api/token/", {"username": "yuri", "password": "salah12345"}, format="json"
        )
        self.assertEqual(response.status_code, 401)


class RegisterTests(APITestCase):
    def register(self, **extra):
        body = {"name": "Meila", "email": "meila@example.com", "password": "rahasia123", **extra}
        return self.client.post("/api/users/register/", body, format="json")

    def test_register_with_username(self):
        response = self.register(username="Meila_A")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(User.objects.filter(username="meila_a").exists())

    def test_register_with_username_only_no_name(self):
        response = self.client.post(
            "/api/users/register/",
            {"username": "mhs01", "email": "mhs01@example.com", "password": "rahasia123"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        login = self.client.post(
            "/api/token/", {"username": "mhs01", "password": "rahasia123"}, format="json"
        )
        self.assertEqual(login.data["user"]["name"], "mhs01")

    def test_register_without_username_uses_email(self):
        self.assertEqual(self.register().status_code, 201)
        self.assertTrue(User.objects.filter(username="meila@example.com").exists())

    def test_username_validation(self):
        User.objects.create_user(username="dipakai", email="x@example.com", password="rahasia123")
        self.assertEqual(self.register(username="dipakai").status_code, 400)
        self.assertEqual(self.register(username="pakai@email").status_code, 400)
        self.assertEqual(self.register(username="ab").status_code, 400)


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="yuri", email="yuri@example.com", password="rahasia123", first_name="Yuri"
        )
        User.objects.create_user(username="meila", email="meila@example.com", password="rahasia123")

    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/users/me/").status_code, 401)

    def test_get_and_update_profile(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get("/api/users/me/").data["username"], "yuri")

        response = self.client.patch(
            "/api/users/me/",
            {"name": "Yuri Elva", "username": "Yuri.Elva", "email": "Yuri.Baru@Example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["name"], "Yuri Elva")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "yuri.elva")
        self.assertEqual(self.user.email, "yuri.baru@example.com")

    def test_cannot_take_other_users_username_or_email(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(
            self.client.patch("/api/users/me/", {"username": "meila"}, format="json").status_code, 400
        )
        self.assertEqual(
            self.client.patch("/api/users/me/", {"email": "meila@example.com"}, format="json").status_code,
            400,
        )
        # Akun lama (username = email) tetap bisa menyimpan tanpa mengganti username.
        old = User.objects.create_user(username="lama@example.com", email="lama@example.com", password="x12345678")
        self.client.force_authenticate(old)
        self.assertEqual(
            self.client.patch(
                "/api/users/me/", {"name": "Lama", "username": "lama@example.com"}, format="json"
            ).status_code,
            200,
        )
        self.client.force_authenticate(self.user)
        # Username/email sendiri tetap boleh dikirim ulang.
        self.assertEqual(
            self.client.patch("/api/users/me/", {"username": "yuri"}, format="json").status_code, 200
        )


class ChangePasswordTests(APITestCase):
    URL = "/api/users/me/password/"

    def setUp(self):
        self.user = User.objects.create_user(username="yuri", email="yuri@example.com", password="lama12345")
        self.client.force_authenticate(self.user)

    def test_change_password(self):
        response = self.client.post(
            self.URL, {"current_password": "lama12345", "new_password": "baru12345"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("baru12345"))

    def test_rejects_wrong_current_short_or_same_password(self):
        for body in (
            {"current_password": "salah1234", "new_password": "baru12345"},
            {"current_password": "lama12345", "new_password": "pendek"},
            {"current_password": "lama12345", "new_password": "lama12345"},
        ):
            self.assertEqual(self.client.post(self.URL, body, format="json").status_code, 400, body)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("lama12345"))

    def test_requires_login(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post(self.URL, {}, format="json").status_code, 401)
