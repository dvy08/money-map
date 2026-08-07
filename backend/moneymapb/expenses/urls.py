from django.urls import path
from .views import (
    ExpenseCategoryListCreateView, ExpenseCategoryDetailView,
    ExpenseCategoryAmountSpentForMonthView,
    ExpenseListCreateView, ExpenseDetailView,
    ExpenseAmountSpentForMonthView,
    FixedExpenseScheduleListCreateView, FixedExpenseScheduleDetailView,
    FixedExpenseScheduleGetOccurancesBetweenView
)

urlpatterns = [
    path('categories/', ExpenseCategoryListCreateView.as_view(), name='expense_category_list'),
    path('categories/<int:pk>/', ExpenseCategoryDetailView.as_view(), name='expense_category_detail'),
    path('categories/<int:pk>/amount-spent-for-month/', ExpenseCategoryAmountSpentForMonthView.as_view(), name="expense_category_amount_spent_for_month" ),
    path('individual/', ExpenseListCreateView.as_view(), name='expense_list'),
    path('individual/<int:pk>/', ExpenseDetailView.as_view(), name='expense_detail'),
    path('individual/<int:pk>/amount-spent-for-month/', ExpenseAmountSpentForMonthView.as_view(), name="expense_amount_spent_for_month"),
    path('schedules/', FixedExpenseScheduleListCreateView.as_view(), name='fixed_expense_schedule_list'),
    path('schedules/<int:pk>/', FixedExpenseScheduleDetailView.as_view(), name='fixed_expense_schedule_detail'),
    path('schedules/<int:pk>/get-occurances-between/', FixedExpenseScheduleGetOccurancesBetweenView.as_view(), name='fixed_expense_schedule_get_occurances_between')
]