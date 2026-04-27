from django.apps import AppConfig


class XeonConfig(AppConfig):
    name = 'xeon'

    def ready(self):
        print("----> XeonConfig ready() is running! Signals loaded.")
        import xeon.signals
