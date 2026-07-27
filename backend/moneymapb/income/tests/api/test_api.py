from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase

from income.models import IncomeSource

User = get_user_model()

class IncomeSourceAPITests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@test.com",
            password="Pass1234word"
        )

        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@test.com",
            password="Pass1234word"
        )

    ## AUTH & PERMISSIONS
    def test_unauthenticated_user_cannot_get_income_source(self):
        response = self.client.get(
            "/api/income/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_income_source(self):
        response = self.client.post(
            "/api/income/",
            {
                "name": "Salary",
                "budgeted_amount": "25000.00",
                "has_goal": False
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_income_source(self):

        IncomeSource.objects.create(
            user=self.user1,
            name="Salary",
            budgeted_amount=Decimal("25000.00")
        )

        IncomeSource.objects.create(
            user=self.user2,
            name="Freelance",
            budgeted_amount=Decimal("5000.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/income/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Salary")

    def test_user_cannot_access_other_users_income_source(self):
        source2 = IncomeSource.objects.create(
            user=self.user2,
            name="Freelance",
            budgeted_amount=Decimal("5000.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/income/{source2.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_income_source(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/income/",
            {
                "name": "Salary",
                "budgeted_amount": "25000.00",
                "has_goal": False
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IncomeSource.objects.count(), 1)
    
    def test_user_can_get_income_sources(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/income/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_income_source(self):
        self.client.force_authenticate(
            user = self.user1
        )

        source = IncomeSource.objects.create(
            user=self.user1,
            name="Salary",
            budgeted_amount=Decimal("25000.00")
        )

        response = self.client.get(
            f"/api/income/{source.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_income_source(self):
        source = IncomeSource.objects.create(
            user=self.user1,
            name="Salary",
            budgeted_amount=Decimal("25000.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/income/{source.id}/",
            {
                "name": "Updated Salary",
                "budgeted_amount": "30000.00",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_income_source(self):
        source = IncomeSource.objects.create(
            user=self.user1,
            name="Salary",
            budgeted_amount=Decimal("25000.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/income/{source.id}/",
            {
                "budgeted_amount": "30000.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_income_source(self):
        source = IncomeSource.objects.create(
            user=self.user1,
            name="Salary",
            budgeted_amount=Decimal("25000.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/income/{source.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(IncomeSource.objects.count(), 0)