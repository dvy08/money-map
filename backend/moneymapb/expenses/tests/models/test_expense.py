from django.test import TestCase
from expenses.models import ExpenseCategory, Expense
from transactions.models import Transactions
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
            budgeted_amount = Decimal("200.00")
        )

        cls.transaction1 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense,
            amount = Decimal("100.00"),
            description = "First half of netflix bill - JUN",
            transaction_date = date(2026, 6, 2)
        )

        cls.transaction2 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense,
            amount = Decimal("150.00"),
            description = "Second half of netflix bill _ JUN",
            transaction_date = date(2026, 6, 5)
        )

        cls.transaction3 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense,
            amount = Decimal("100.00"),
            description = "First half of netflix bill - MAY",
            transaction_date = date(2026, 5, 5)
        )

    def test_create_expense(self):
        self.assertEqual(self.expense.name, 'Netflix')
        self.assertEqual(self.expense.expense_type, 'fixed')

    def test_expense_belongs_to_user(self):
        self.assertEqual(self.expense.user, self.user)

    def test_expense_has_category(self):
        self.assertEqual(self.expense.category, self.category)

    def test_str(self):
        self.assertEqual(str(self.expense.expense_type), 'fixed')

    def test_amount_spent_for_month_returns_zero_with_no_transactions(self):
        self.assertEqual(self.expense.amount_spent_for_month(8, 2026), Decimal("0.00"))

    def test_amount_spent_for_month_sums_transactions_for_specific_month(self):
        self.assertEqual(self.expense.amount_spent_for_month(6, 2026), Decimal("250.00"))

    def test_amount_spent_for_current_month_returns_zero_with_no_transactions(self):
        self.assertEqual(self.expense.amount_spent_for_current_month, Decimal("0.00"))

    def test_amount_spent_for_current_month_sums_transactions(self):
        today = date.today()

        Transactions.objects.create(
            user = self.user,
            expense = self.expense,
            amount = Decimal("100.00"),
            description = "First half of netflix bill",
            transaction_date = date(today.year, today.month, today.day)
        )

        Transactions.objects.create(
            user = self.user,
            expense = self.expense,
            amount = Decimal("100.00"),
            description = "Second half of netflix bill",
            transaction_date = date(today.year, today.month, today.day)
        )

        self.assertEqual(self.expense.amount_spent_for_current_month, Decimal("200.00"))
    
    def test_is_over_budget_false(self):
        self.assertFalse(self.expense.is_over_budget)

    def test_is_over_budget_true(self):
        today = date.today()

        Transactions.objects.create(
            user = self.user,
            expense = self.expense,
            amount = Decimal("150.00"),
            description = "First half of netflix bill",
            transaction_date = date(today.year, today.month, today.day)
        )

        Transactions.objects.create(
            user = self.user,
            expense = self.expense,
            amount = Decimal("120.00"),
            description = "Second half of netflix bill",
            transaction_date = date(today.year, today.month, today.day)
        )

        self.assertTrue(self.expense.is_over_budget)

