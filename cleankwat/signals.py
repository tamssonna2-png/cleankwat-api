from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdminProfile, ClientProfile, CollectorProfile, User, UserRole


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    if instance.role == UserRole.CLIENT:
        ClientProfile.objects.get_or_create(user=instance)
    elif instance.role == UserRole.COLLECTOR:
        CollectorProfile.objects.get_or_create(
            user=instance,
            defaults={"badge_code": f"COL-{str(instance.id)[:8].upper()}"},
        )
    elif instance.role == UserRole.ADMIN:
        AdminProfile.objects.get_or_create(user=instance)