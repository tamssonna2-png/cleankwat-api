from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CollectionPointViewSet,
    CollectorTaskViewSet,
    MeView,
    RegisterView,
    ServicePlanListView,
    SubscriptionViewSet,
    ZoneListView,
)

router = DefaultRouter()
router.register("points", CollectionPointViewSet, basename="collection-point")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")
router.register("collector/tasks", CollectorTaskViewSet, basename="collector-task")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("zones/", ZoneListView.as_view(), name="zones"),
    path("plans/", ServicePlanListView.as_view(), name="plans"),
    path("", include(router.urls)),
]