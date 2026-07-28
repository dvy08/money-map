from django.test import TestCase
from transactions.models import Transactions
from income.models import IncomeSource
from expenses.models import Expense, ExpenseCategory
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()

class TransactionsModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='test1',
            password='Pass1234word'
        )
        cls.source = IncomeSource.objects.create(
            user=cls.user,
            name='Salary',
            budgeted_amount=Decimal("30000.00")
        )
        cls.category = ExpenseCategory.objects.create(
            user=cls.user,
            name="Groceries"
        )
        cls.expense = Expense.objects.create(
            user=cls.user,
            category = cls.category,
            name = 'Cereal',
            expense_type = 'variable',
            budgeted_amount = 200.00
        )

    def test_create_income_transaction(self):
        transaction = Transactions.objects.create(
            user=self.user,
            amount=Decimal("20000.00"),
            transaction_date=date(2026, 6, 2),
            description="Partial Salary",
            transaction_type=Transactions.TransactionType.INCOME,
            income_source=self.source
        )

        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal("20000.00"))
        self.assertEqual(transaction.transaction_date, date(2026, 6, 2))
        self.assertEqual(transaction.description, "Partial Salary")
        self.assertEqual(transaction.transaction_type, Transactions.TransactionType.INCOME)
        self.assertEqual(transaction.income_source, self.source)

    def test_create_expense_transaction(self):
        transaction = Transactions.objects.create(
            user=self.user,
            amount=Decimal("400.00"),
            transaction_date=date(2026, 6, 2),
            description="Bulk Cereal",
            transaction_type=Transactions.TransactionType.EXPENSE,
            expense=self.expense
        )

        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal("400.00"))
        self.assertEqual(transaction.transaction_date, date(2026, 6, 2))
        self.assertEqual(transaction.description, "Bulk Cereal")
        self.assertEqual(transaction.transaction_type, Transactions.TransactionType.EXPENSE)
        self.assertEqual(transaction.expense, self.expense)
