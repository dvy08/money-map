from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import IncomeSource
from .serializers import IncomeSourceSerializer

# Create your views here.

class IncomeSourceListCreateView(generics.ListCreateAPIView):
    serializer_class = IncomeSourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IncomeSource.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class IncomeSourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IncomeSourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IncomeSource.objects.filter(
            user=self.request.user
        )
