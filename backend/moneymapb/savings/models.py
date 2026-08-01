from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator
from transactions.models import Transactions

# Create your models here.

class Savings(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings'
    )
    fund_name = models.CharField(max_length=100)
    initial_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    budgeted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    has_goal = models.BooleanField(default=False)
    goal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        blank=True,
        null=True
    )
    start_date = models.DateField(
        null=True,
        blank=True
    )
    target_date = models.DateField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.fund_name
    
    @property
    def balance(self):
        total = Transactions.objects.filter(
            savings = self
        ).aggregate(
            total = Sum("amount") 
        )["total"] or Decimal("0.00")

        total = self.initial_amount + total

        return total or Decimal("0.00")
    
    @property
    def amount_remaining(self):
        if not (self.has_goal):
            return Decimal("0.00")
        
        remaining = self.goal_amount - self.balance
        return max(remaining, Decimal("0.00"))
    
    @property
    def minimum_monthly_payment(self):
        if not (self.has_goal):
            return Decimal("0.00")
        
        today = timezone.now().date()

        months_remaining = ((self.target_date.year - today.year) * 12
        + (self.target_date.month - today.month)
        )

        if months_remaining <= 0:
            return self.amount_remaining
        
        return self.amount_remaining / Decimal(months_remaining)
    
    @property
    def is_goal_reached(self):
        if not (self.has_goal):
            return False
        
        return self.balance >= (self.goal_amount or Decimal("0.00"))
    