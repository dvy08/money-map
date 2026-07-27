from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Transactions
from .serializers import TransactionsSerializer

# Create your views here.

class TransactionsListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transactions.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class TransactionsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transactions.objects.filter(
            user=self.request.user
        )

