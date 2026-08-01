from rest_framework import serializers
from .models import Expense, ExpenseCategory, FixedExpenseSchedule

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ["id", "user", "created_at"]

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ["id", "user", "created_at"]

class FixedExpenseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedExpenseSchedule
        fields = '__all__'
        read_only_fields = ["id", "created_at"]
