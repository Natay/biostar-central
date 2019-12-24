import logging
from django.db.models.signals import post_migrate
from django.conf import settings
from django.apps import AppConfig

logger = logging.getLogger('engine')


class ChatConfig(AppConfig):
    name = 'biostar.chat'

    def ready(self):
        pass
