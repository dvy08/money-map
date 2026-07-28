from rest_framework import serializers
from .models import Expense, ExpenseCategory, FixedExpenseSchedule

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ["user"]

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ["user"]

class FixedExpenseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedExpenseSchedule
        fields = '__all__'
