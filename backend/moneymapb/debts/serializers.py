from rest_framework import serializers
from .models import Debts

class DebtsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Debts
        fields='__all__'
        read_only_fields = ["id", "user", "created_at", "updated_at"]