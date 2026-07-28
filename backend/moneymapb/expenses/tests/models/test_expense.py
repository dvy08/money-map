from django.test import TestCase
from expenses.models import ExpenseCategory, Expense
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()

class ExpenseModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser1',
            email='testuser1@test.com',
            password='Pass1234word'
        )

        cls.category = ExpenseCategory.objects.create(
            user = cls.user,
            name = 'Subscriptions'
        )

        cls.expense = Expense.objects.create(
            user = cls.user,
            category = cls.category,
            name = 'Netflix',
            expense_type = 'fixed',
            budgeted_amount = 200.00
        )

    def test_create_expense(self):
        self.assertEqual(self.expense.name, 'Netflix')
        self.assertEqual(self.expense.expense_type, 'fixed')

    def test_expense_belongs_to_user(self):
        self.assertEqual(self.expense.user, self.user)

    def test_expense_has_category(self):
        self.assertEqual(self.expense.category, self.category)