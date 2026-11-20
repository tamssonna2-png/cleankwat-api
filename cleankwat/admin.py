from django.contrib import admin
from .models import (
    AdminProfile,
    ClientProfile,
    CollectionPoint,
    CollectionTask,
    CollectorProfile,
    ServicePlan,
    Subscription,
    User,
    Vehicle,
    Zone,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("phone", "full_name", "email")


admin.site.register(AdminProfile)
admin.site.register(ClientProfile)
admin.site.register(CollectorProfile)
admin.site.register(Zone)
admin.site.register(Vehicle)
admin.site.register(ServicePlan)
admin.site.register(CollectionPoint)
admin.site.register(Subscription)
admin.site.register(CollectionTask)