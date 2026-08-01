from django.test import TestCase
from savings.models import Savings
from transactions.models import Transactions
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()

class IncomeSourceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser1',
            password='Pass1234word'
        )

        cls.savings = Savings.objects.create(
            user=cls.user,
            fund_name='Emergency',
            initial_amount=Decimal("0.00"),
            budgeted_amount=Decimal("100.00")
        )

    def test_create_savings_fund(self):
        self.assertEqual(self.savings.user, self.user)
        self.assertEqual(self.savings.fund_name, 'Emergency')
        self.assertEqual(self.savings.budgeted_amount, Decimal("100.00"))

    def test_savings_fund_default_values(self):
        self.assertFalse(self.savings.has_goal)
        self.assertIsNone(self.savings.goal_amount)
        self.assertIsNone(self.savings.start_date)
        self.assertIsNone(self.savings.target_date)

    def test_savings_fund_str(self):
        self.assertEqual(str(self.savings), "Emergency")

    def test_savings_fund_goal(self):
        savings = Savings.objects.create(
            user=self.user,
            fund_name='Holiday',
            initial_amount=Decimal("100.00"),
            budgeted_amount=Decimal("100.00"),
            has_goal=True,
            goal_amount=Decimal("5000.00"),
            start_date=date(2026, 8, 8),
            target_date=date(2028, 9, 1)
        )

        self.assertTrue(savings.has_goal)
        self.assertEqual(savings.goal_amount, Decimal("5000.00"))
        self.assertEqual(savings.start_date, date(2026, 8, 8))
        self.assertEqual(savings.target_date, date(2028, 9, 1))

    ##BALANCE
    def test_balance_only_aggregates_own_transactions(self):
        savings1 = Savings.objects.create(
            user=self.user,
            fund_name='Holiday- Italy',
            initial_amount=Decimal("0.00"),
            budgeted_amount=Decimal("200.00")
        )

        Transactions.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=savings1
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("200.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )

        self.assertEqual(self.savings.balance, Decimal("200.00"))

    def test_balance_zero_when_no_transactions_or_initial_amount(self):
        self.assertEqual(self.savings.balance, Decimal("0.00"))

    def test_balance_includes_transactions_and_initial_amount(self):
        self.savings.initial_amount = Decimal("300.00")

        Transactions.objects.create(
            user=self.user,
            amount=Decimal("200.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("200.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )

        self.assertEqual(self.savings.balance, Decimal("700.00"))

    def test_balance_with_just_initial_amount(self):
        self.savings.initial_amount = Decimal("300.00")

        self.assertEqual(self.savings.balance, Decimal("300.00"))

    ##AMOUNT_REMAINING
    def test_amount_remaining_zero_when_has_goal_is_false(self):
        self.assertEqual(self.savings.amount_remaining, Decimal("0.00"))

    def test_amount_remaining_when_goal_not_reached(self):
        self.savings.has_goal = True
        self.savings.goal_amount = Decimal("10000.00")

        self.assertEqual(self.savings.amount_remaining, Decimal("10000.00"))

    def test_amount_remaining_never_negative(self):
        self.savings.has_goal = True
        self.savings.goal_amount = Decimal("10000.00")

        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10500.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )

        self.assertEqual(self.savings.amount_remaining, Decimal("0.00"))

    ##MINIMUM_MONTHLY_PAYMENT
    def test_minimum_monthly_payment_returns_zero_when_goal_is_false(self):
        self.assertEqual(self.savings.minimum_monthly_payment, Decimal("0.00"))

    def test_minimum_monthly_payment_calculated_correctly(self):
        today = timezone.now().date()

        target = today.replace(
            year=today.year + 1
        )

        min = Savings.objects.create(
            user=self.user,
            fund_name='Holiday',
            initial_amount=Decimal("2000.00"),
            budgeted_amount=Decimal("500.00"),
            has_goal=True,
            goal_amount=Decimal("14000.00"),
            target_date=target
        )

        self.assertEqual(min.minimum_monthly_payment, Decimal("1000.00"))

    def test_minimum_monthly_payment_returns_amount_remaining_when_target_date_is_today(self):
        today = timezone.now().date()
        
        min = Savings.objects.create(
            user=self.user,
            fund_name='Holiday',
            initial_amount=Decimal("2000.00"),
            budgeted_amount=Decimal("500.00"),
            has_goal=True,
            goal_amount=Decimal("14000.00"),
            target_date=today
        )
        
        self.assertEqual(min.minimum_monthly_payment, min.amount_remaining)

    def test_minimum_monthly_payment_returns_amount_remaining_when_target_date_has_passed(self):
        past_date = timezone.now().date() - timedelta(days=30)
        
        min = Savings.objects.create(
            user=self.user,
            fund_name='Holiday',
            initial_amount=Decimal("2000.00"),
            budgeted_amount=Decimal("500.00"),
            has_goal=True,
            goal_amount=Decimal("14000.00"),
            target_date=past_date
        )
        
        self.assertEqual(min.minimum_monthly_payment, min.amount_remaining)

    ##IS_GOAL_REACHED
    def test_is_goal_not_reached_when_has_goal_is_false(self):
        self.assertFalse(self.savings.is_goal_reached)

    def test_is_goal_not_reached_false(self):
        self.savings.has_goal = True
        self.savings.goal_amount = Decimal("10000.00")

        self.assertFalse(self.savings.is_goal_reached)

    def test_is_goal_reached_true_when_balance_equal_goal(self):
        self.savings.has_goal = True
        self.savings.goal_amount = Decimal("10000.00")

        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )

        self.assertTrue(self.savings.is_goal_reached)

    def test_is_goal_reached_true_when_balance_exceeds_goal(self):
        self.savings.has_goal = True
        self.savings.goal_amount = Decimal("10000.00")

        Transactions.objects.create(
            user=self.user,
            amount=Decimal("15000.00"),
            transaction_date=date.today(),
            transaction_type="savings",
            savings=self.savings
        )

        self.assertTrue(self.savings.is_goal_reached)
