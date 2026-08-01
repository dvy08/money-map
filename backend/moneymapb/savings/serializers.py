from rest_framework import serializers
from .models import Savings

class SavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Savings
        fields='__all__'
        read_only_fields = ["id", "user", "created_at", "updated_at"]