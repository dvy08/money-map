from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase
from datetime import date
from decimal import Decimal

from transactions.models import Transactions
from income.models import IncomeSource

User = get_user_model()
    
class TransactionsAPITests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@test.com",
            password="Pass1234word"
        )

        cls.income_source1 = IncomeSource.objects.create(
            user=cls.user1,
            name='Salary',
            budgeted_amount=Decimal("30000.00")
        )

        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@test.com",
            password="Pass1234word"
        )

        cls.income_source2 = IncomeSource.objects.create(
            user=cls.user2,
            name='Tips',
            budgeted_amount=Decimal("10000.00")
        )
    
    ## AUTH & PERMISSIONS
    def test_unauthenticated_user_cannot_get_transactions(self):
        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_transaction(self):
        response = self.client.post(
            "/api/transactions/",
            {
                "amount": "2000.00",
                "transaction_date": "2026-07-01",
                "description": "Partial Tip",
                "transaction_type": "income"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_transactions(self):
        Transactions.objects.create(
            user=self.user1,
            amount=Decimal("30000.00"),
            transaction_date=date(2026, 7, 1),
            description="Salary",
            transaction_type="income",
            income_source=self.income_source1
        )

        Transactions.objects.create(
            user=self.user2,
            amount=Decimal("200.00"),
            transaction_date=date(2026, 7, 1),
            description="Tips",
            transaction_type="income",
            income_source=self.income_source2
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["amount"], '30000.00')

    def test_transaction_belongs_to_logged_in_user(self):
        transaction=Transactions.objects.create(
            user=self.user2,
            amount=Decimal("200.00"),
            transaction_date=date(2026, 7, 1),
            description="Tips",
            transaction_type="income",
            income_source=self.income_source2
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/transactions/{transaction.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_transaction(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/transactions/",
            {
                "amount": "20000.00",
                "transaction_date": "2026-07-01",
                "description": "Partial Salary",
                "transaction_type": "income",
                "income_source": self.income_source1.id
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transactions.objects.count(), 1)

    def test_user_can_get_transactions(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_transaction(self):
        transaction=Transactions.objects.create(
            user=self.user1,
            amount=Decimal("30000.00"),
            transaction_date=date(2026, 7, 1),
            description="Salary",
            transaction_type="income",
            income_source=self.income_source1
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/transactions/{transaction.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_transaction(self):
        transaction=Transactions.objects.create(
            user=self.user1,
            amount=Decimal("30000.00"),
            transaction_date=date(2026, 7, 1),
            description="Salary",
            transaction_type="income",
            income_source=self.income_source1
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/",
            {
                "transaction_date": "2026-07-14"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_transaction(self):
        transaction=Transactions.objects.create(
            user=self.user1,
            amount=Decimal("30000.00"),
            transaction_date=date(2026, 7, 1),
            description="Salary",
            transaction_type="income",
            income_source=self.income_source1
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/transactions/{transaction.id}/",
            {
                "amount": "20000.00",
                "transaction_date": "2026-07-01",
                "description": "Partial Salary",
                "transaction_type": "income",
                "income_source": self.income_source1.id
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_transaction(self):
        transaction=Transactions.objects.create(
            user=self.user1,
            amount=Decimal("30000.00"),
            transaction_date=date(2026, 7, 1),
            description="Salary",
            transaction_type="income",
            income_source=self.income_source1
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/transactions/{transaction.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transactions.objects.count(), 0)