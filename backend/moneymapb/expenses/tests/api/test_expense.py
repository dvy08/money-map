from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase

from expenses.models import ExpenseCategory, Expense

User = get_user_model()

class ExpenseAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@test.com",
            password="Pass1234word"
        )

        cls.category1 = ExpenseCategory.objects.create(
            user=cls.user1,
            name="Groceries"
        )

        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@test.com",
            password="Pass1234word"
        )

        cls.category2 = ExpenseCategory.objects.create(
            user=cls.user2,
            name="Rent"
        )
    
    ## AUTH & PERMISSIONS
    def test_unauthenticated_user_cannot_get_expenses(self):
        response = self.client.get(
            "/api/expenses/individual/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_expense(self):
        response = self.client.post(
            "/api/expenses/individual/",
            {
                "name": "Netflix",
                "expense_type": "fixed",
                "budgeted_amount": "200.00"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_expenses(self):
        Expense.objects.create(
            user=self.user1,
            category = self.category1,
            name = 'Basics',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )

        Expense.objects.create(
            user=self.user2,
            category = self.category2,
            name = 'First Half',
            expense_type = 'fixed',
            budgeted_amount = 2000.00
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/expenses/individual/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Basics")

    def test_expenses_belongs_to_logged_in_user(self):
        expense2=Expense.objects.create(
            user=self.user2,
            category = self.category2,
            name = 'First Half',
            expense_type = 'fixed',
            budgeted_amount = 2000.00
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/expenses/individual/{expense2.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_expense(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/expenses/individual/",
            {
                "category": self.category1.id,
                "name": "Lunches",
                "expense_type": "variable",
                "budgeted_amount": "200.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)

    def test_user_can_get_expenses(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/api/expenses/individual/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_expense(self):
        expense = Expense.objects.create(
            user=self.user1,
            category = self.category1,
            name = 'Lunch',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/expenses/individual/{expense.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_expense(self):
        expense = Expense.objects.create(
            user=self.user1,
            category = self.category1,
            name = 'Lunch',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/expenses/individual/{expense.id}/",
            {
                "name": "Breakfasts"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_expense(self):
        expense = Expense.objects.create(
            user=self.user1,
            category = self.category1,
            name = 'Lunch',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/expenses/individual/{expense.id}/",
            {
                "category": self.category1.id,
                "name": "Breakfasts",
                "expense_type": "variable",
                "budgeted_amount": "200.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_expense(self):
        expense = Expense.objects.create(
            user=self.user1,
            category = self.category1,
            name = 'Basics',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/expenses/individual/{expense.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Expense.objects.count(), 0)