from django.test import TestCase
from income.models import IncomeSource
from transactions.models import Transactions
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

    ##TOTAL_RECEIVED_LIFETIME
    def test_total_received_lifetime_aggregates_only_own_transactions(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1
        )

        self.assertEqual(self.source.total_received_lifetime, Decimal("5000.00"))   

    def test_total_received_lifetime_returns_zero_when_no_transactions(self):
        self.assertEqual(self.source.total_received_lifetime, Decimal("0.00"))

    def test_total_received_lifetime_returns_sum_of_all_transactions(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date(2025, 2, 15),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertEqual(self.source.total_received_lifetime, Decimal("25000.00"))

    ##TOTAL_RECEIVED_FOR_CURRENT_MONTH
    def test_total_received_for_current_month_aggregates_only_own_transactions(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1
        )
    
        self.assertEqual(self.source.total_received_for_current_month, Decimal("5000.00"))

    def test_total_received_for_current_month_returns_zero_when_no_transactions(self):
        self.assertEqual(self.source.total_received_for_current_month, Decimal("0.00"))
    
    def test_total_received_for_current_month_returns_only_totals_of_current_month(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date(2025, 7, 25),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertEqual(self.source.total_received_for_current_month, Decimal("20000.00"))
    
    ##TOTAL_RECEIVED_FOR_MONTH
    def test_total_received_for_month_aggregates_only_own_transactions(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1
        )
    
        self.assertEqual(
            self.source.total_received_for_month(date.today().year, date.today().month), Decimal("5000.00")
            )

    def test_total_received_for_month_returns_zero_when_no_transactions(self):
        self.assertEqual(self.source.total_received_for_month(2026, 1), Decimal("0.00"))
    
    def test_total_received_for_month_returns_only_totals_for_month(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date(2025, 3, 15),
            transaction_type="income",
            income_source=self.source,
        )
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date(2025, 3, 25),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertEqual(self.source.total_received_for_month(2025, 3), Decimal("25000.00"))
    
    ##IS_OVER_BUDGET
    def test_is_over_budget_false_when_under_budget(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertFalse(self.source.is_over_budget)
    
    def test_is_over_budget_false_when_exact(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("25000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertFalse(self.source.is_over_budget)
    
    def test_is_over_budget_true(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("35000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertTrue(self.source.is_over_budget)
            
    ##MONTHLY_GOAL_PROGRESS
    def test_monthly_goal_progress_returns_zero_when_goal_is_disabled(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("15000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source,
        )
    
        self.assertEqual(self.source.monthly_goal_progress, Decimal("0.00"))
    
    def test_monthly_goal_progress_returns_percentage(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertEqual(self.source1.monthly_goal_progress, Decimal("50.00"))
    
    def test_monthly_goal_progress_rounds_to_two_decimal_places(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("12333.66"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertEqual(self.source1.monthly_goal_progress, Decimal("61.67"))
    
    ##MONTHLY_GOAL_COMPLETED
    def test_monthly_goal_completed_returns_false_when_not_met(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("5000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertFalse(self.source1.monthly_goal_completed)
    
    def test_monthly_goal_completed_returns_true_when_met(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertTrue(self.source1.monthly_goal_completed)
    
    def test_monthly_goal_completed_returns_true_when_exceeded(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("30000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertTrue(self.source1.monthly_goal_completed)
    
    ##AMOUNT_TO_MONTHLY_GOAL
    def test_amount_to_monthly_goal_returns_remaining_amount(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("10000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertEqual(self.source1.amount_to_monthly_goal, Decimal("10000.00"))
    
    def test_amount_to_monthly_goal_returns_zero_when_goal_met(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )
    
        self.assertEqual(self.source1.amount_to_monthly_goal, Decimal("0.00"))
    
    def test_amount_to_monthly_goal_returns_zero_when_goal_exceeded(self):
        Transactions.objects.create(
            user=self.user,
            amount=Decimal("30000.00"),
            transaction_date=date.today(),
            transaction_type="income",
            income_source=self.source1,
        )

        self.assertEqual(self.source1.amount_to_monthly_goal, Decimal("0.00"))
    
