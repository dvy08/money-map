from django.test import TestCase
from expenses.models import ExpenseCategory, Expense, FixedExpenseSchedule
from datetime import date
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class FixedBillScheduleModelTests(TestCase):

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

        cls.fixed_expense_schedule = FixedExpenseSchedule.objects.create(
            expense = cls.expense,
            start_date = date(2025, 7, 25)
        )

    def test_create_fixed_expense_schedule(self):
        self.assertEqual(self.fixed_expense_schedule.expense, self.expense)
        self.assertEqual(self.fixed_expense_schedule.start_date, date(2025, 7, 25))
    
    def test_default_values(self):
        self.assertEqual(self.fixed_expense_schedule.frequency, FixedExpenseSchedule.Frequency.MONTHLY)
        self.assertIsNone(self.fixed_expense_schedule.reccurance_days)

    def test_custome_values(self):
        expense = Expense.objects.create(
            user = self.user,
            category = self.category,
            name = 'Adobe',
            expense_type = 'fixed',
            budgeted_amount = 300.00
        )

        schedule = FixedExpenseSchedule.objects.create(
            expense = expense,
            frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS,
            reccurance_days = 14,
            start_date = date(2026, 7, 16)
        )

        self.assertEqual(schedule.frequency, FixedExpenseSchedule.Frequency.EVERY_X_DAYS)
        self.assertEqual(schedule.reccurance_days, 14)

    def test_expense_can_only_have_one_schedule(self):
        with self.assertRaises(IntegrityError):
            FixedExpenseSchedule.objects.create(
            expense = self.expense,
            frequency = 'monthly',
            start_date = date(2026, 7, 15)
        )