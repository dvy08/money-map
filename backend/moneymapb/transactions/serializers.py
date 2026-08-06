from rest_framework import serializers
from .models import Transactions

class TransactionsSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True
    )

    class Meta:
        model = Transactions
        fields = [
            "id",
            "user",
            "amount",
            "transaction_date",
            "description",
            "transaction_type",
            "transaction_type_display",
            "income_source",
            "expense",
            "savings",
            "debts",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        transaction_type = attrs.get("transaction_type")

        mapping = {
            "income": "income_source",
            "expense": "expense",
            "savings": "savings",
            "debts": "debts"
        }

        required_field = mapping.get(transaction_type)

        for field in mapping.values():
            if field != required_field and attrs.get(field):
                raise serializers.ValidationError(
                    {field: f"{field} should only be set for its matching transaction type."}
                )

        if required_field and not attrs.get(required_field):
            raise serializers.ValidationError(
                {required_field: f"{required_field} is required for {transaction_type} transactions."}
            )

        return attrs