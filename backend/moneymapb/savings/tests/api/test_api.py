from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase
from decimal import Decimal

from savings.models import Savings

User = get_user_model()
    
class SavingsAPITests(APITestCase):
    
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
    def test_unauthenticated_user_cannot_get_savings_funds(self):
        response = self.client.get(
            "/api/savings/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_savings_fund(self):
        response = self.client.post(
            "/api/savings/",
            {
                "fund_name": "Emergency",
                "initial_amount": "100.00",
                "budgeted_amount": "200.00"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_savings_funds(self):
        Savings.objects.create(
            user=self.user1,
            fund_name='Emergency',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00")
        )

        Savings.objects.create(
            user=self.user2,
            fund_name='Holiday',
            initial_amount=Decimal("0.00"),
            budgeted_amount=Decimal("400.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/savings/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["budgeted_amount"], '100.00')

    def test_savings_fund_belongs_to_logged_in_user(self):
        savings=Savings.objects.create(
            user=self.user2,
            fund_name='Holiday',
            initial_amount=Decimal("0.00"),
            budgeted_amount=Decimal("400.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/savings/{savings.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_savings_fund(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/savings/",
            {
                "user": self.user1.id,
                "fund_name": "Emergency",
                "initial_amount": "100.00",
                "budgeted_amount": "200.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Savings.objects.count(), 1)

    def test_user_can_get_savings_funds(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/api/savings/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_savings_fund(self):
        savings=Savings.objects.create(
            user=self.user1,
            fund_name='Emergency',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00")
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/savings/{savings.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_savings_fund(self):
        savings=Savings.objects.create(
            user=self.user1,
            fund_name='Emergency',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/savings/{savings.id}/",
            {
                "fund_name": "Emergency - Car"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_savings_fund(self):
        savings=Savings.objects.create(
            user=self.user1,
            fund_name='Emergency',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/savings/{savings.id}/",
            {
                "user": self.user1.id,
                "fund_name": "Emergency - Car",
                "initial_amount": "100.00",
                "budgeted_amount": "200.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_savings_fund(self):
        savings=Savings.objects.create(
            user=self.user1,
            fund_name='Emergency',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/savings/{savings.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Savings.objects.count(), 0)