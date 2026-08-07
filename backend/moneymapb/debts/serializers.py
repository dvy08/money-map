from rest_framework import serializers
from .models import Debts

class DebtsSerializer(serializers.ModelSerializer):
    balance = serializers.ReadOnlyField()
    total_paid = serializers.ReadOnlyField()
    repayment_progress = serializers.ReadOnlyField()
    credit_utilization = serializers.ReadOnlyField()

    class Meta:
        model=Debts
        fields=[
            "id",
            "expense",
            "name",
            "minimum_payment",
            "credit_limit",
            "interest_rate",
            "initial_balance",
            "budgeted_amount",
            "balance",
            "total_paid",
            "repayment_progress",
            "credit_utilization",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]