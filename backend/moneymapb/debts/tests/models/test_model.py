from django.test import TestCase
from debts.models import Debts
from transactions.models import Transactions
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, datetime
from django.utils import timezone
from unittest.mock import patch


User = get_user_model()

class DebtsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser1',
            password='Pass1234word'
        )

        cls.debt = Debts.objects.create(
            user=cls.user,
            name='Car Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )

        cls.debt1 = Debts.objects.create(
            user=cls.user,
            name='Student Loan',
            minimum_payment=Decimal("100.00"),
            credit_limit=Decimal("20000.00"),
            interest_rate=Decimal("10.00"),
            initial_balance=Decimal("3000.00"),
            budgeted_amount=Decimal("200.00")
        )

        cls.transaction1 = Transactions.objects.create(
            user = cls.user,
            debts = cls.debt,
            amount = Decimal("100.00"),
            description = "Car Loan",
            transaction_date = date(2026, 5, 3)
        )

        cls.transaction2 = Transactions.objects.create(
            user = cls.user,
            debts = cls.debt,
            amount = Decimal("100.00"),
            description = "Car Loan",
            transaction_date = date(2026, 6, 3)
        )

        cls.transaction3 = Transactions.objects.create(
            user = cls.user,
            debts = cls.debt,
            amount = Decimal("100.00"),
            description = "Car Loan",
            transaction_date = date(2026, 7, 3)
        )

    def test_debt_creation(self):
        self.assertEqual(self.debt.user, self.user)
        self.assertEqual(self.debt.name, 'Car Loan')
        self.assertEqual(self.debt.minimum_payment, Decimal("100.00"))
        self.assertEqual(self.debt.credit_limit, Decimal("20000.00"))
        self.assertEqual(self.debt.interest_rate, Decimal("10.00"))
        self.assertEqual(self.debt.initial_balance, Decimal("3000.00"))
        self.assertEqual(self.debt.budgeted_amount, Decimal("200.00"))


    ##BALANCE
    @patch("debts.models.timezone.now")
    def test_balance_after_one_month_no_transactions_with_interest(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 30)
        )

        self.debt1.refresh_from_db()
        
        self.debt1.created_at = datetime(2026, 7, 1)

        self.assertEqual(self.debt1.balance, Decimal("3025.00"))

    @patch("debts.models.timezone.now")
    def test_balance_after_interest_compounds_multiple_months(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 9, 1)
        )

        self.debt1.refresh_from_db()
        
        self.debt1.created_at = datetime(2026, 7, 1)

        self.assertEqual(self.debt1.balance, Decimal("3075.63"))

    @patch("debts.models.timezone.now")
    def test_balance_multiple_payments_in_a_single_month(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 29)
        )

        self.debt.refresh_from_db()

        self.debt.created_at = datetime(2026, 5, 1)

        Transactions.objects.create(
            user = self.user,
            debts = self.debt,
            amount = Decimal("100.00"),
            description = "Car Loan",
            transaction_date = date(2026, 7, 4)
        )

        self.assertEqual(self.debt.balance, Decimal("2673.12"))

    @patch("debts.models.timezone.now")
    def test_balance_payments(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 1)
        )

        self.debt.refresh_from_db()

        self.debt.created_at = datetime(2026, 5, 1)

        self.assertEqual(
            self.debt.balance, Decimal("2773.12")
        )

    @patch("debts.models.timezone.now")
    def test_balance_never_negative(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 8, 1)
        )
        
        self.debt1.refresh_from_db()

        self.debt1.created_at = datetime(2026, 7, 1)

        Transactions.objects.create(
            user = self.user,
            debts = self.debt1,
            amount = Decimal("4000.00"),
            description = "Car Loan",
            transaction_date = date(2026, 7, 3)
        )

        self.assertEqual(self.debt1.balance, Decimal("0.00"))

    ##TOTAL_PAID
    def test_total_paid_zero_with_no_transactions(self):
        self.assertEqual(self.debt1.total_paid, Decimal("0.00"))

    def test_total_paid_with_transactions(self):
        self.assertEqual(self.debt.total_paid, Decimal("300.00"))

    ##REPAYMENT_PROGRESS
    def test_repayment_progress_is_zero_with_no_transactions(self):
        self.assertEqual(self.debt1.repayment_progress, Decimal("0.00"))

    @patch("debts.models.timezone.now")
    def test_repayment_progress_with_transactions(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 1)
        )
                
        self.debt.refresh_from_db()
        
        self.debt.created_at = datetime(2026, 5, 1)

        self.assertEqual(self.debt.repayment_progress, Decimal("7.6"))

    @patch("debts.models.timezone.now")
    def test_repayment_progress_never_negative(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 10, 1)
        )

        self.debt1.refresh_from_db()

        self.debt1.created_at = datetime(2026, 5, 1)

        self.assertEqual(self.debt1.repayment_progress, Decimal("0.00"))

    ##CREDIT_UTILIZATION
    @patch("debts.models.timezone.now")
    def test_credit_utilization(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 1)
        )

        self.debt.refresh_from_db()
                
        self.debt.created_at = datetime(2026, 5, 1)

        self.assertEqual(self.debt.credit_utilization, Decimal("13.9"))

    @patch("debts.models.timezone.now")
    def test_credit_utilization_without_transactions(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 1)
        )

        self.debt1.refresh_from_db()
                
        self.debt1.created_at = datetime(2026, 5, 1)

        self.assertEqual(self.debt1.credit_utilization, Decimal("15.4"))

    @patch("debts.models.timezone.now")
    def test_credit_utilization_never_negative(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 7, 1)
        )

        self.debt1.refresh_from_db()
                
        self.debt1.created_at = datetime(2026, 7, 1)

        Transactions.objects.create(
            user = self.user,
            debts = self.debt1,
            amount = Decimal("4000.00"),
            description = "Car Loan",
            transaction_date = date(2026, 7, 3)
        )

        self.assertEqual(self.debt1.credit_utilization, Decimal("0.0"))