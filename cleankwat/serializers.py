from rest_framework import serializers
from .models import (
    CollectionPoint,
    CollectionTask,
    ServicePlan,
    Subscription,
    User,
    UserRole,
    Zone,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name", "password", "role"]
        read_only_fields = ["id"]

    def validate_role(self, value):
        # Empêche l'auto-inscription directe en ADMIN via l'API publique
        if value == UserRole.ADMIN:
            raise serializers.ValidationError("Impossible de créer un compte ADMIN par inscription publique.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class MeSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name", "role", "profile"]

    def get_profile(self, obj: User):
        if obj.role == UserRole.CLIENT and hasattr(obj, "client_profile"):
            return {
                "wallet_balance": str(obj.client_profile.wallet_balance),
                "rating": obj.client_profile.rating,
            }
        if obj.role == UserRole.COLLECTOR and hasattr(obj, "collector_profile"):
            p = obj.collector_profile
            return {
                "badge_code": p.badge_code,
                "is_available": p.is_available,
                "assigned_vehicle_id": str(p.assigned_vehicle_id) if p.assigned_vehicle_id else None,
            }
        if obj.role == UserRole.ADMIN and hasattr(obj, "admin_profile"):
            return {"department": obj.admin_profile.department}
        return {}


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ["id", "name", "city"]


class ServicePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlan
        fields = ["id", "name", "plan_type", "pickups_per_week", "base_price"]


class CollectionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPoint
        fields = ["id", "client", "zone", "label", "latitude", "longitude", "estimated_weight_kg"]
        read_only_fields = ["id", "client"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "client",
            "collection_point",
            "plan",
            "preferred_days",
            "start_date",
            "end_date",
            "status",
        ]
        read_only_fields = ["id", "client", "status"]


class CollectionTaskSerializer(serializers.ModelSerializer):
    point_label = serializers.CharField(source="collection_point.label", read_only=True)
    latitude = serializers.FloatField(source="collection_point.latitude", read_only=True)
    longitude = serializers.FloatField(source="collection_point.longitude", read_only=True)

    class Meta:
        model = CollectionTask
        fields = [
            "id",
            "subscription",
            "collection_point",
            "point_label",
            "latitude",
            "longitude",
            "collector",
            "vehicle",
            "scheduled_date",
            "status",
            "completed_at",
        ]
        read_only_fields = ["id", "subscription", "collection_point", "collector", "vehicle", "scheduled_date", "completed_at"]