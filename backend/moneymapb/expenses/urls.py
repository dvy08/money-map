from django.urls import path
from .views import (
    ExpenseCategoryListCreateView, ExpenseCategoryDetailView,
    ExpenseListCreateView, ExpenseDetailView,
    FixedExpenseScheduleListCreateView, FixedExpenseScheduleDetailView
)

urlpatterns = [
    path('categories/', ExpenseCategoryListCreateView.as_view(), name='expense_category_list'),
    path('categories/<int:pk>/', ExpenseCategoryDetailView.as_view(), name='expense_category_detail'),
    path('individual/', ExpenseListCreateView.as_view(), name='expense_list'),
    path('individual/<int:pk>/', ExpenseDetailView.as_view(), name='expense_detail'),
    path('schedules/', FixedExpenseScheduleListCreateView.as_view(), name='fixed_expense_schedule_list'),
    path('schedules/<int:pk>/', FixedExpenseScheduleDetailView.as_view(), name='fixed_expense_schedule_detail'),
]