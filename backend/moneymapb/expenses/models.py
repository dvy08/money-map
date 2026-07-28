from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum
from datetime import date, timedelta
import calendar

# Create your models here.

class ExpenseCategory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):

    class ExpenseType(models.TextChoices):
        FIXED = 'fixed', 'Fixed'
        VARIABLE = 'variable', 'Variable'
        TAX = 'tax', 'Tax'

    class ExpenseWantVNeed(models.TextChoices):
        WANT = 'want', 'Want'
        NEED = 'need', 'Need'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    name = models.CharField(
        max_length=100,
        blank=True
    )
    expense_type = models.CharField(
        max_length=20,
        choices=ExpenseType.choices
    )
    budgeted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    want_v_need = models.CharField(
        max_length=20,
        choices=ExpenseWantVNeed.choices,        
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.expense_type

class FixedExpenseSchedule(models.Model):

    class Frequency(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        EVERY_X_DAYS = 'every x days', 'Every X Days'

    expense = models.OneToOneField(
        Expense,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.MONTHLY
    )
    reccurance_days = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.frequency