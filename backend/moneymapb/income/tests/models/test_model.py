from django.test import TestCase
from income.models import IncomeSource
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()

class IncomeSourceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser1',
            password='Pass1234word'
        )

        cls.source = IncomeSource.objects.create(
            user=cls.user,
            name='Salary',
            budgeted_amount=Decimal("25000.00")
        )

        cls.source1 = IncomeSource.objects.create(
            user=cls.user,
            name='Bi-Weekly Pay',
            budgeted_amount=Decimal("10000.00"),
            has_goal = True,
            goal_amount=Decimal("20000.00")
        )

    
    def test_create_income_source(self):
        self.assertEqual(self.source.user, self.user)
        self.assertEqual(self.source.name, 'Salary')
        self.assertEqual(self.source.budgeted_amount, Decimal("25000.00"))

    def test_has_goal_default_values(self):
        self.assertFalse(self.source.has_goal)
        self.assertIsNone(self.source.goal_amount)

    def test_income_source_str(self):
        self.assertEqual(str(self.source), "Salary")

    def test_income_source_goal(self):
        source = IncomeSource.objects.create(
            user=self.user,
            name='Freelance Work',
            budgeted_amount=Decimal("5000.00"),
            has_goal=True,
            goal_amount=Decimal("10000.00")
        )

        self.assertTrue(source.has_goal)
        self.assertEqual(source.goal_amount, Decimal("10000.00"))
