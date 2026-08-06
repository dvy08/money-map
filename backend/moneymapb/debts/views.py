from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Debts
from .serializers import DebtsSerializer

# Create your views here.

class DebtsListCreateView(generics.ListCreateAPIView):
    serializer_class = DebtsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Debts.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class DebtsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DebtsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Debts.objects.filter(
            user=self.request.user
        )
