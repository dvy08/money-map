from rest_framework import serializers
from .models import Expense, ExpenseCategory, FixedExpenseSchedule

class ExpenseCategorySerializer(serializers.ModelSerializer):
    budgeted_amount = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = ExpenseCategory
        fields =[
            "id",
            "name",
            "budgeted_amount",
            "is_over_budget",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]

class ExpenseSerializer(serializers.ModelSerializer):
    amount_spent_for_current_month = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()

    class Meta:
        model = Expense
        fields =[
            "id",
            "category",
            "name",
            "expense_type",
            "budgeted_amount",
            "want_v_need",
            "amount_spent_for_current_month",
            "is_over_budget",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]

class FixedExpenseScheduleSerializer(serializers.ModelSerializer):
    due_date = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = FixedExpenseSchedule
        fields =[
            "id",
            "expense",
            "frequency",
            "reccurance_days",
            "start_date",
            "due_date",
            "days_until_due",
            "is_overdue",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]
