from django.urls import path
from .views import DebtsListCreateView, DebtsDetailView

urlpatterns = [
    path('', DebtsListCreateView.as_view(), name='debts_list'),
    path('<int:pk>/', DebtsDetailView.as_view(), name='debts_detail')
]