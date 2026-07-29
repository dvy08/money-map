from django.test import TestCase
from expenses.models import ExpenseCategory, Expense, FixedExpenseSchedule
from datetime import date
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from unittest.mock import patch

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

 ##MONTHLY - DUE_DATE
    def test_due_date_returns_current_month(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 10)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            self.fixed_expense_schedule.start_date = date(2026, 1, 15)
            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 7, 15))

    def test_due_date_rolls_to_next_month_when_due_date_passes(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 20)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            self.fixed_expense_schedule.start_date = date(2026, 1, 15)

            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 8, 15))

    def test_due_date_rolls_to_next_year(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 12, 20)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            self.fixed_expense_schedule.start_date = date(2026, 1, 15)

            self.assertEqual(self.fixed_expense_schedule.due_date, date(2027, 1, 15))

    def test_due_date_handles_short_months(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 2, 10)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            self.fixed_expense_schedule.start_date = date(2026, 1, 31)
            
            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 2, 28))

    ##EVERY X DAYS DUE_DATE
    def test_every_x_days_returns_next_due_date(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 18)

            self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
            self.fixed_expense_schedule.start_date = date(2026, 7, 1)
            self.fixed_expense_schedule.reccurance_days = 10

            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 7, 21))

    def test_every_x_days_returns_start_date_when_too_early_to_process(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 1)

            self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
            self.fixed_expense_schedule.start_date = date(2026, 7, 10)
            self.fixed_expense_schedule.reccurance_days = 7

            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 7, 10))

    def test_every_x_days_handles_multiple_cycles(self):
        with patch("expenses.models.date") as mock_date:
            mock_date.today.return_value = date(2026, 8, 1)

            self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
            self.fixed_expense_schedule.start_date = date(2026, 7, 1)
            self.fixed_expense_schedule.reccurance_days = 10

            self.assertEqual(self.fixed_expense_schedule.due_date, date(2026, 8, 10))

    ##GET_DUE_DATE_FOR_MONTH
    def test_get_due_date_for_month_returns_correct_date(self):
        self.fixed_expense_schedule.start_date = date(2026, 1, 15)

        self.assertEqual(self.fixed_expense_schedule.get_due_date_for_month(8, 2026), date(2026, 8, 15))

    def test_get_due_date_for_month_handles_short_months(self):
        self.fixed_expense_schedule.start_date = date(2026, 1, 31)

        self.assertEqual(self.fixed_expense_schedule.get_due_date_for_month(2, 2026), date(2026, 2, 28))

    def test_get_due_date_for_month_returns_none_for_every_x_days(self):
        self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS

        self.assertIsNone(self.fixed_expense_schedule.get_due_date_for_month(2, 2026))

    ##GET_OCCURANCES_BETWEEN - MONTHLY
    def test_monthly_occurances_single_month(self):
        self.fixed_expense_schedule.start_date = date(2026, 1, 15)
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 8, 1), date(2026, 8, 31))
        )

        self.assertEqual(occurances, [date(2026, 8, 15)])

    def test_monthly_occurances_over_multiple_months(self):
        self.fixed_expense_schedule.start_date = date(2026, 1, 15)
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 8, 1), date(2026, 10, 31))
        )

        self.assertEqual(occurances, [date(2026, 8, 15), date(2026, 9, 15), date(2026, 10, 15)])

    def test_monthly_occurances_can_return_empty_list(self):
        self.fixed_expense_schedule.start_date = date(2026, 1, 15)
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 8, 1), date(2026, 8, 10))
        )

        self.assertEqual(occurances, [])

    ##GET_OCCURANCES_BETWEEN - EVERY X DAYS
    def test_every_x_days_occurances(self):
        self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
        self.fixed_expense_schedule.start_date = date(2026, 7, 1)
        self.fixed_expense_schedule.reccurance_days = 10
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 8, 1), date(2026, 8, 31))
        )

        self.assertEqual(occurances, [date(2026, 8, 10), date(2026, 8, 20), date(2026, 8, 30)])

    def test_every_x_days_returns_empty_list(self):
        self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
        self.fixed_expense_schedule.start_date = date(2026, 1, 1)
        self.fixed_expense_schedule.reccurance_days = 30
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 1, 2), date(2026, 1, 15))
        )

        self.assertEqual(occurances, [])

    def test_every_x_days_includes_start_date(self):
        self.fixed_expense_schedule.frequency = FixedExpenseSchedule.Frequency.EVERY_X_DAYS
        self.fixed_expense_schedule.start_date = date(2026, 8, 1)
        self.fixed_expense_schedule.reccurance_days = 10
        occurances = (
            self.fixed_expense_schedule.get_occurances_between(date(2026, 8, 1), date(2026, 8, 31))
        )

        self.assertIn(date(2026, 8, 1), occurances)