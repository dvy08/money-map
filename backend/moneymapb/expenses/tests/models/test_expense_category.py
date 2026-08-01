from django.test import TestCase
from expenses.models import ExpenseCategory, Expense
from transactions.models import Transactions
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

        cls.category1 = ExpenseCategory.objects.create(
            user = cls.user,
            name = 'Groceries'
        )

        cls.category2 = ExpenseCategory.objects.create(
            user = cls.user,
            name = 'Utilities'
        )        

        cls.expense1 = Expense.objects.create(
            user = cls.user,
            category = cls.category1,
            name = 'Cereal',
            expense_type = 'variable',
            budgeted_amount = Decimal("200.00")
        )

        cls.expense2 = Expense.objects.create(
            user = cls.user,
            category = cls.category1,
            name = 'Meat',
            expense_type = 'variable',
            budgeted_amount = Decimal("500.00")
        )

        cls.transaction1 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense1,
            amount = Decimal("150.00"),
            description = "Cornflakes, muesli",
            transaction_date = date(2026, 6, 5)
        )

        cls.transaction2 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense2,
            amount = Decimal("400.00"),
            description = "Steak, sausage",
            transaction_date = date(2026, 6, 5)
        )

        cls.transaction3 = Transactions.objects.create(
            user = cls.user,
            expense = cls.expense2,
            amount = Decimal("100.00"),
            description = "Chicken",
            transaction_date = date(2026, 5, 5)
        )        

    def test_create_category(self):
        self.assertEqual(self.category1.name, 'Groceries')

    def test_category_belongs_to_user(self):
        self.assertEqual(self.category1.user, self.user)

    def test_category_str(self):    
        self.assertEqual(str(self.category1), 'Groceries')

    ##METHODS
    def test_amount_spent_for_month_only_aggregates_own_transactions(self):
        expense = Expense.objects.create(
            user = self.user,
            category = self.category2,
            name = 'Rent',
            expense_type = 'Fixed',
            budgeted_amount = Decimal("5000.00")
        )
        Transactions.objects.create(
            user = self.user,
            expense = expense,
            amount = Decimal("1500.00"),
            description = "Utilities - Rent",
            transaction_date = date(2026, 6, 5)
        ) 

        self.assertEqual(self.category2.amount_spent_for_month(6, 2026), Decimal("1500.00")) 

    def test_budgeted_amount_only_calculates_own_expenses(self):
        Expense.objects.create(
            user = self.user,
            category = self.category2,
            name = 'Rent',
            expense_type = 'Fixed',
            budgeted_amount = Decimal("5000.00")
        )  

        self.assertEqual(self.category1.budgeted_amount, Decimal("700.00"))
        
    def test_amount_spent_for_month_returns_zero_with_no_transactions(self):
        self.assertEqual(self.category1.amount_spent_for_month(2, 2026), Decimal("0.00"))

    def test_amount_spent_for_month_sums_transactions_for_specific_month(self):
        self.assertEqual(self.category1.amount_spent_for_month(6, 2026), Decimal("550.00"))

    def test_budgeted_amount_month_sums_bill_budgets(self):
        self.assertEqual(self.category1.budgeted_amount, Decimal("700.00"))
    
    def test_budgeted_amount_returns_zero_with_no_bills(self):
        self.assertEqual(self.category2.budgeted_amount, Decimal("0.00"))

    def test_is_over_budget_false(self):
        self.assertFalse(self.category1.is_over_budget)

    def test_is_over_budget_true(self):
        today = date.today()

        Transactions.objects.create(
            user = self.user,
            expense = self.expense2,
            amount = Decimal("900.00"),
            description = "Steak, sausage",
            transaction_date = today
        )
        self.assertTrue(self.category1.is_over_budget)
