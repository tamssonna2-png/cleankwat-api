from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CollectionPoint,
    CollectionTask,
    ServicePlan,
    Subscription,
    TaskStatus,
    Zone,
)
from .permissions import IsClient, IsCollector
from .serializers import (
    CollectionPointSerializer,
    CollectionTaskSerializer,
    MeSerializer,
    RegisterSerializer,
    ServicePlanSerializer,
    SubscriptionSerializer,
    ZoneSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


class ZoneListView(generics.ListAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.AllowAny]


class ServicePlanListView(generics.ListAPIView):
    queryset = ServicePlan.objects.all()
    serializer_class = ServicePlanSerializer
    permission_classes = [permissions.AllowAny]


class CollectionPointViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionPointSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return CollectionPoint.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Subscription.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class CollectorTaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CollectionTaskSerializer
    permission_classes = [IsCollector]

    def get_queryset(self):
        return CollectionTask.objects.filter(collector=self.request.user).order_by("scheduled_date")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = TaskStatus.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])
        return Response(CollectionTaskSerializer(task).data, status=status.HTTP_200_OK)