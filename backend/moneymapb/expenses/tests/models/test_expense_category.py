from django.test import TestCase
from expenses.models import ExpenseCategory
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()

class ExpenseCategoryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='Pass1234word'
        )

        cls.category = ExpenseCategory.objects.create(
            user = cls.user,
            name = 'Groceries'
        )

    def test_create_category(self):
        self.assertEqual(self.category.name, 'Groceries')

    def test_category_belongs_to_user(self):
        self.assertEqual(self.category.user, self.user)
