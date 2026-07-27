from django.urls import path
from .views import TransactionsListCreateView, TransactionsDetailView

urlpatterns = [
    path('', TransactionsListCreateView.as_view(), name='transactions_list'),
    path('<int:pk>/', TransactionsDetailView.as_view(), name='transactions_detail')
]