# Inherit from the main settings file.

# Inherit from the accounts settings file.
from biostar.accounts.settings import *

# Django debug flag.
DEBUG = True

SITE_NAME = 'Biostar Chat'

ENABLE_CHAT = True

CHAT_APP = [
    'biostar.chat.apps.ChatConfig',
    'channels'
]


ASGI_APPLICATION = 'biostar.chat.routing.application'

# Enable/disable async chat
ASYNC_CHAT = False
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

INSTALLED_APPS = DEFAULT_APPS + CHAT_APP + ACCOUNTS_APPS + EMAILER_APP

ROOT_URLCONF = 'biostar.chat.urls'

WSGI_APPLICATION = 'biostar.wsgi.application'

# Tries to load up secret settings from a predetermined module
# This is for convenience only!
try:
    from conf.run.secrets import *
    print(f"Loaded secrets from: conf.run.secrets")
except Exception as exc:
    print(f"Secrets module not imported: {exc}")

