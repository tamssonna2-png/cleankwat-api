from django.apps import AppConfig


class CleankwatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cleankwat'

    def ready(self):
        import cleankwat.signals