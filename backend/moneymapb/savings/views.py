from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Savings
from .serializers import SavingsSerializer

# Create your views here.

class SavingsListCreateView(generics.ListCreateAPIView):
    serializer_class = SavingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Savings.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class SavingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Savings.objects.filter(
            user=self.request.user
        )