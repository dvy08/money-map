from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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