from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase
from decimal import Decimal

from debts.models import Debts

User = get_user_model()
    
class DebtsAPITests(APITestCase):
    
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
    def test_unauthenticated_user_cannot_get_debts(self):
        response = self.client.get(
            "/api/debts/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_debts(self):
        response = self.client.post(
            "/api/debts/",
            {
                "name": "Car Loan",
                "minimum_payment": "100.00",
                "credit_limit": "20000.00",
                "interest_rate": "10.00",
                "initial_balance": "3000.00",
                "budgeted_amount": "250.00"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_debts(self):
        Debts.objects.create(
            user=self.user1,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )

        Debts.objects.create(
            user=self.user2,
            name='Student Loan',
            minimum_payment=Decimal("150.00"),
            credit_limit=Decimal("30000.00"),
            interest_rate=Decimal("12.00"),
            initial_balance=Decimal("5000.00"),
            budgeted_amount=Decimal("250.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/debts/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["budgeted_amount"], '200.00')

    def test_debt_belongs_to_logged_in_user(self):
        debt=Debts.objects.create(
            user=self.user2,
            name='Student Loan',
            minimum_payment=Decimal("150.00"),
            credit_limit=Decimal("30000.00"),
            interest_rate=Decimal("12.00"),
            initial_balance=Decimal("5000.00"),
            budgeted_amount=Decimal("250.00")
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/debts/{debt.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_debts(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/debts/",
            {
                "user": self.user1.id,
                "name": "Car Loan",
                "minimum_payment": "100.00",
                "credit_limit": "20000.00",
                "interest_rate": "10.00",
                "initial_balance": "3000.00",
                "budgeted_amount": "250.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Debts.objects.count(), 1)

    def test_user_can_get_debts(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/api/debts/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_debt(self):
        debt=Debts.objects.create(
            user=self.user1,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/debts/{debt.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_debt(self):
        debt=Debts.objects.create(
            user=self.user1,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/debts/{debt.id}/",
            {
                "name": "New Car Loan"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_debts(self):
        debt=Debts.objects.create(
            user=self.user1,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/debts/{debt.id}/",
            {
                "user": self.user1.id,
                "name": "New Car Loan",
                "minimum_payment": "150.00",
                "credit_limit": "25000.00",
                "interest_rate": "11.00",
                "initial_balance": "3500.00",
                "budgeted_amount": "200.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_debt(self):
        debt=Debts.objects.create(
            user=self.user1,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/debts/{debt.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Debts.objects.count(), 0)