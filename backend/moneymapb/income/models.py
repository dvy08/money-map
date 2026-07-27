from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from datetime import date

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
