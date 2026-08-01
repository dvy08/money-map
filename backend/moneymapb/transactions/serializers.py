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
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

        def validate(self, attrs):
            transaction_type = attrs.get("transaction_type")
            income_source = attrs.get("income_source")

            if (
                transaction_type == transaction_type.TransactionType.INCOME and not income_source
            ):
                raise serializers.ValidationError(
                    {
                        "income_source": (
                            "Income transactions must have an income source"
                        )
                    }
                )
            return attrs