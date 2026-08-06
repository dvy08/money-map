from django.db import models
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator
from transactions.models import Transactions

# Create your models here.

class Debts(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debts"
    )
    name = models.CharField(max_length=100)
    minimum_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    interest_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    budgeted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def balance(self):
        balance = Decimal(self.initial_balance)

        monthly_rate = (
            Decimal(self.interest_rate) / Decimal("100.00")
        ) / Decimal("12.00")

        transactions = Transactions.objects.filter(
            debts = self
        ).order_by("transaction_date")

        payments_by_month = {}

        for tx in transactions:
            key = (tx.transaction_date.year, tx.transaction_date.month)
            payments_by_month.setdefault(key, Decimal("0.00"))
            payments_by_month[key] += Decimal(tx.amount)

        start_year = self.created_at.year
        start_month = self.created_at.month

        today = timezone.now().date()

        if today.month == 1:
            end_year = today.year - 1
            end_month = 12
        else:
            end_year = today.year
            end_month = today.month 

        year = start_year
        month = start_month

        while (year, month) <= (end_year, end_month):
            interest = (balance * monthly_rate).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            balance += interest

            balance = balance.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            balance -= payments_by_month.get(
                (year, month),
                Decimal("0.00")
            )

            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

        return max(balance, Decimal("0.00"))

    @property
    def total_paid(self):
        total = Transactions.objects.filter(
            debts=self
        ).aggregate(
            total = Sum("amount")
        )["total"]

        return total or Decimal("0.00")

    @property
    def repayment_progress(self):
        progress = (self.balance / self.initial_balance * Decimal("100.00")).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP
        )

        return max(Decimal("100.00") - progress, Decimal("0.0"))

    @property
    def credit_utilization(self):
        utilization = (self.balance / self.credit_limit * Decimal("100.00")).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP
        )

        return max(utilization, Decimal("0.0"))


