from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from transactions.models import Transactions
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

    def __str__(self):
        return self.name
    
    def amount_spent_for_month(self, month, year):
        return( 
            Transactions.objects.filter(
                expense__category=self,
                transaction_date__year=year,
                transaction_date__month=month
            ).aggregate(
                total = Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

    @property
    def budgeted_amount(self):
        return (
            self.expenses.aggregate(
              total = Sum("budgeted_amount")
            )["total"]
            or Decimal("0.00")
        )
    
    @property
    def is_over_budget(self):
        today = date.today()
        return self.amount_spent_for_month(today.month, today.year) > self.budgeted_amount

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

    def amount_spent_for_month(self, month, year):
        total = Transactions.objects.filter(
            transaction_date__year=year,
            transaction_date__month=month
        ).aggregate(
            total = Sum("amount")
        )["total"]

        return total or Decimal("0.00")
    
    @property
    def amount_spent_for_current_month(self):
        today = date.today()

        total = Transactions.objects.filter(
            transaction_date__year=today.year,
            transaction_date__month=today.month
        ).aggregate(
            total = Sum("amount")
        )["total"]

        return total or Decimal("0.00")
    
    @property
    def is_over_budget(self):
        return self.amount_spent_for_current_month > self.budgeted_amount

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
    
    @property
    def due_date(self):
        today = date.today()

        if self.frequency == self.Frequency.MONTHLY:
            year = today.year
            month = today.month

            due_day = min(
                self.start_date.day,
                calendar.monthrange(year, month)[1]
            )

            current_due = date(year, month, due_day)

            if current_due >= today:
                return current_due
            
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

            due_day = min(
                self.start_date.day,
                calendar.monthrange(year, month)[1]
            )
            
            return date(year, month, due_day)
        
        if self.frequency == self.Frequency.EVERY_X_DAYS:
            next_due = self.start_date

            while next_due < today:
                next_due += timedelta(
                    days= self.reccurance_days
                )

            return next_due
        
    @property
    def days_until_due(self):
        return (self.due_date - date.today()).days
    
    @property
    def is_paid_this_month(self):
        due = self.due_date

        return Transactions.objects.filter(
            transaction_date__year=due.year,
            transaction_date__month=due.month
        ).exists()
    
    @property
    def is_overdue(self):
        return self.days_until_due < 0
    
    def get_due_date_for_month(self, month, year):
        if self.frequency != self.Frequency.MONTHLY:
            return None
        
        due_day = min(
            self.start_date.day,
            calendar.monthrange(year, month)[1]
        )
        
        return date(year, month, due_day)

    
    def get_occurances_between(self, start_date, end_date):
        occurances = []

        if self.frequency == self.Frequency.MONTHLY:
            current_year = start_date.year
            current_month = start_date.month

            while True: 
                due_date = self.get_due_date_for_month(
                    current_month, current_year
                )

                if due_date > end_date:
                    break

                if due_date >= start_date:
                    occurances.append(due_date)

                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month +=1

        elif self.frequency == self.Frequency.EVERY_X_DAYS:
            current = self.start_date

            while current < start_date:
                current += timedelta(
                    days=self.reccurance_days
                )
            
            while current <= end_date:
                occurances.append(current)

                current += timedelta(
                    days=self.reccurance_days
                )

        return occurances