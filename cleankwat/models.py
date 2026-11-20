import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrateur"
    CLIENT = "CLIENT", "Client"
    COLLECTOR = "COLLECTOR", "Éboueur"


class PlanType(models.TextChoices):
    STANDARD = "STANDARD", "Standard"
    VIP = "VIP", "VIP"
    EXPRESS = "EXPRESS", "Express"


class SubscriptionStatus(models.TextChoices):
    PENDING_PAYMENT = "PENDING_PAYMENT", "En attente de paiement"
    ACTIVE = "ACTIVE", "Actif"
    EXPIRED = "EXPIRED", "Expiré"
    CANCELLED = "CANCELLED", "Annulé"


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    IN_PROGRESS = "IN_PROGRESS", "En cours"
    COMPLETED = "COMPLETED", "Collecté"
    MISSED = "MISSED", "Manqué"


class UserManager(BaseUserManager):
    def create_user(self, phone: str, full_name: str, password: str | None = None, **extra_fields):
        if not phone:
            raise ValueError("Le numéro de téléphone est obligatoire.")
        user = self.model(phone=phone, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, full_name: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        return self.create_user(phone, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.role})"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    department = models.CharField(max_length=100, default="Operations")


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.FloatField(default=5.0)


class Zone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, default="Yaoundé")


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plate_number = models.CharField(max_length=25, unique=True)
    capacity_kg = models.FloatField()
    is_operational = models.BooleanField(default=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="vehicles")


class CollectorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="collector_profile")
    badge_code = models.CharField(max_length=30, unique=True)
    is_available = models.BooleanField(default=True)
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collectors",
    )


class CollectionPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collection_points")
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="collection_points")
    label = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    estimated_weight_kg = models.FloatField(default=10.0)


class ServicePlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    pickups_per_week = models.PositiveSmallIntegerField(default=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    collection_point = models.ForeignKey(CollectionPoint, on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(ServicePlan, on_delete=models.PROTECT)
    preferred_days = models.JSONField(default=list)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.PENDING_PAYMENT)


class CollectionTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="tasks")
    collection_point = models.ForeignKey(CollectionPoint, on_delete=models.PROTECT, related_name="tasks")
    collector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collector_tasks",
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_date = models.DateField()
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    completed_at = models.DateTimeField(null=True, blank=True)