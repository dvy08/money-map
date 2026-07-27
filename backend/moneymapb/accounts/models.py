from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    class IncomeType(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        WEEKLY = 'weekly', 'Weekly'
        BIWEEKLY = 'biweekly', 'Bi-Weekly'
        IRREGULAR = 'irregular', 'Irregular'
        SEASONAL = 'seasonal', 'Seasonal'

    class Currencies(models.TextChoices):
        USD = 'USD', 'US Dollar'
        EUR = 'EUR', 'Euro'
        GBP = 'GBP', 'British Pound'
        ZAR = 'ZAR', 'South African Rand'

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False
    )

    income_type = models.CharField(
        max_length=15,
        choices=IncomeType.choices,
        default=IncomeType.MONTHLY
    )

    tax_allotment_needed=models.BooleanField(default=False)

    currency=models.CharField(
        max_length=3,
        choices=Currencies.choices,
        default=Currencies.ZAR
    )

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username