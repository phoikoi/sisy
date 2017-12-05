from django.apps import AppConfig
from django.conf import settings

class SisyConfig(AppConfig):
    name = 'sisy'
    def ready(self):
        import sisy.signals
