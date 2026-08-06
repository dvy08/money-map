from django.db import models
from django.conf import settings

# Create your models here.
class Transactions(models.Model):

    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"
        SAVINGS = "savings", "SAVINGS"
        DEBT = "debt", "Debt"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    transaction_date = models.DateField()
    description = models.CharField(
        max_length=255,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    income_source = models.ForeignKey(
        "income.IncomeSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    savings = models.ForeignKey(
        "savings.Savings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    debts = models.ForeignKey(
        "debts.Debts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-transaction_date"]