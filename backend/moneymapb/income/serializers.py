from rest_framework import serializers
from .models import IncomeSource

class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = '__all__'
        read_only_fields=["id", "user", "created_at", "updated_at"]