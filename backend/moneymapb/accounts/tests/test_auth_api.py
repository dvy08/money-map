from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationTests(APITestCase):
    
    def test_user_can_register(self):
        response = self.client.post(
            '/api/accounts/register/',
            {
                "first_name": "test1first",
                "second_name": "test1last",
                "username": "test1",
                "email": "test1@test.com",
                "password": "Pass1234word",
                "income_type": "monthly",
                "currency": "ZAR"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_password_with_no_uppercase_rejected(self):
        response = self.client.post(
            '/api/accounts/register/',
            {
                "first_name": "testfirst",
                "second_name": "testlast",
                "username": "test11",
                "email": "test11@test.com",
                "password": "pass1234word",
                "income_type": "monthly",
                "currency": "ZAR"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("uppercase", str(response.data["password"]).lower())
    
    def test_password_with_no_number_rejected(self):
        response = self.client.post(
            '/api/accounts/register/',
            {
                "first_name": "testfirst",
                "second_name": "testlast",
                "username": "test12",
                "email": "test12@test.com",
                "password": "Passabcword",
                "income_type": "monthly",
                "currency": "ZAR"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("number", str(response.data["password"]).lower())

    def test_password_is_hashed(self):
        self.client.post(
            "/api/accounts/register/",
            {
                "first_name": "testfirst",
                "second_name": "testlast",
                "username": "test2",
                "email": "test2@test.com",
                "password": "Pass1234word"
            }
        )

        user = User.objects.get(username="test2")

        self.assertTrue(user.check_password("Pass1234word"))

    def test_user_can_login(self):
        User.objects.create_user(
            username="test3",
            email="test3@test.com",
            password="Pass1234word"
        )

        response = self.client.post(
            "/api/accounts/token/",
            {
                "username": "test3",
                "password": "Pass1234word"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_login(self):
        response = self.client.post(
            "/api/accounts/token/",
            {
                "username": "test3",
                "password": "Wrongpass1234"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(
            "/api/accounts/me/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = User.objects.create_user(
            username="test4",
            email="test4@test.com",
            password="Pass1234word"
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            "/api/accounts/me/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "test4")

    def test_cannot_register_duplicate_username(self):
        User.objects.create_user(
            username="test5",
            email="test5@test.com",
            password="Pass1234word"
        )

        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "test5",
                "email": "test5sameusername@test.com",
                "password": "Pass1234word"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_cannot_register_duplicate_email(self):
        User.objects.create_user(
            username="JohnTest",
            email="johntest@test.com",
            password="Pass1234word"
        )

        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "JoeTest",
                "email": "johntest@test.com",
                "password": "Pass1234word"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_password_too_short(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "test6",
                "email": "test6@test.com",
                "password": "Pas1"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_refresh_token_returns_new_access_token(self):
        User.objects.create_user(
            username="tokentest",
            email="tokentest@test.com",
            password="Pass1234word"
        )

        login_response = self.client.post(
            "/api/accounts/token/",
            {
                "username": "tokentest",
                "password": "Pass1234word"
            },
            format="json"
        )

        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_invalid_token_rejected(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalidtoken"
        )

        response = self.client.get("/api/accounts/me/")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    