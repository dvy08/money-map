from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

from .models import Expense, ExpenseCategory, FixedExpenseSchedule
from .serializers import ExpenseCategorySerializer, ExpenseSerializer, FixedExpenseScheduleSerializer

# Create your views here.
class ExpenseCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseCategorySerializer

    def get_queryset(self):
        return ExpenseCategory.objects.filter(
            user=self.request.user
        )
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

class ExpenseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExpenseCategory.objects.filter(
            user=self.request.user
        )

class ExpenseCategoryAmountSpentForMonthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        expense_category = ExpenseCategory.objects.get(
            pk=pk,
            user=request.user
        )

        month = int(request.GET.get("month"))
        year = int(request.GET.get("year"))

        amount_spent_for_month = expense_category.amount_spent_for_month(
            month,
            year
        )

        return Response({
            "amount_spent_for_month": amount_spent_for_month
        })

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(
            user=self.request.user
        )
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(
            user=self.request.user
        )

class ExpenseAmountSpentForMonthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        expense = Expense.objects.get(
            pk=pk,
            user=request.user
        )

        month = int(request.GET.get("month"))
        year = int(request.GET.get("year"))

        amount_spent_for_month = expense.amount_spent_for_month(
            month,
            year
        )

        return Response({
            "amount_spent_for_month": amount_spent_for_month
        })

class FixedExpenseScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = FixedExpenseScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FixedExpenseSchedule.objects.filter(
            expense__user = self.request.user
        )
    def perform_create(self, serializer):
        serializer.save()

class FixedExpenseScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FixedExpenseScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FixedExpenseSchedule.objects.filter(
            expense__user = self.request.user
        )

class FixedExpenseScheduleGetOccurancesBetweenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        fixed_expense_schedule = FixedExpenseSchedule.objects.get(
            pk=pk,
            expense__user=self.request.user
        )

        start_date = datetime.strptime(request.GET.get("start_date"), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get("end_date"), '%Y-%m-%d').date()

        get_occurances_between = fixed_expense_schedule.get_occurances_between(
            start_date,
            end_date
        )

        return Response({
            "get_occurances_between": get_occurances_between
        })