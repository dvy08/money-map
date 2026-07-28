from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from datetime import date

from transactions.models import Transactions

# Create your models here.

class IncomeSource(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='income_sources'
    )
    name = models.CharField(max_length=100)
    budgeted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    has_goal = models.BooleanField(default=False)
    goal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    @property
    def total_received_lifetime(self):
        total = Transactions.objects.aggregate(
            total = Sum("amount")
        )["total"]
    
        return total or Decimal("0.00")

    @property
    def total_received_for_current_month(self):
        today = date.today()

        total = Transactions.objects.filter(
            transaction_date__year=today.year,
            transaction_date__month=today.month
        ).aggregate(
            
            total = Sum("amount")
        )["total"]

        return total or Decimal("0.00")

    def total_received_for_month(self, year, month):
        total = Transactions.objects.filter(
            transaction_date__year=year,
            transaction_date__month=month
        ).aggregate(
            
            total = Sum("amount")
        )["total"]

        return total or Decimal("0.00")
    
    @property
    def is_over_budget(self):
        return self.total_received_for_current_month > self.budgeted_amount
    
    @property
    def monthly_goal_progress(self):
        if not self.has_goal or not self.goal_amount:
            return 0
        return round(self.total_received_for_current_month/self.goal_amount * 100, 2)
    
    @property
    def monthly_goal_completed(self):
        if not self.has_goal or not self.goal_amount:
            return False
        return self.total_received_for_current_month >= self.goal_amount
    
    @property
    def amount_to_monthly_goal(self):
        if not self.has_goal or not self.goal_amount:
            return Decimal("0.00")
        remaining = self.goal_amount - self.total_received_for_current_month
        return max(Decimal("0.00"), remaining)