from django.urls import path
from .views import IncomeSourceListCreateView, IncomeSourceDetailView

urlpatterns = [
    path('', IncomeSourceListCreateView.as_view(), name='income_source_list'),
    path('<int:pk>/', IncomeSourceDetailView.as_view(), name='income_source_detail')
]