from django.urls import path
from .views import SavingsListCreateView, SavingsDetailView

urlpatterns = [
    path('', SavingsListCreateView.as_view(), name='savings_funds_list'),
    path('<int:pk>/', SavingsDetailView.as_view(), name='savings_fund_detail')
]