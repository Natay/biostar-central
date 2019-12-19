# Inherit from the main settings file.

# Inherit from the accounts settings file.
from biostar.accounts.settings import *

# Django debug flag.
DEBUG = True

SITE_NAME = 'Biostar Chat'

# Show debug toolbar
DEBUG_TOOLBAR = False

# Override compression if needed.
# COMPRESS_ENABLED = True

ENABLE_CHAT = True

# Log the time for each request
TIME_REQUESTS = True


# Add another context processor to first template.
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'biostar.chat.context.chat'
]

SESSION_UPDATE_SECONDS = 40

SOCIALACCOUNT_EMAIL_VERIFICATION = None
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True

LOGIN_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

SOCIALACCOUNT_ADAPTER = "biostar.accounts.adapter.SocialAccountAdapter"

CHAT_APPS = [
    'biostar.forum.apps.ForumConfig',
    'pagedown',

]

# Additional middleware.
MIDDLEWARE += [
    #'biostar.forum.middleware.user_tasks',
    #'biostar.forum.middleware.benchmark',
]

# Post types displayed when creating, empty list displays all types.
ALLOWED_POST_TYPES = []

# Enable debug toolbar specific functions
if DEBUG_TOOLBAR:
    CHAT_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')


# Import the default pagedown css first, then our custom CSS sheet
# to avoid having to specify all the default styles
PAGEDOWN_WIDGET_CSS = ('pagedown/demo/browser/demo.css', "lib/pagedown.css",)

INSTALLED_APPS = DEFAULT_APPS + CHAT_APPS + ACCOUNTS_APPS + EMAILER_APP

ROOT_URLCONF = 'biostar.forum.urls'

WSGI_APPLICATION = 'biostar.wsgi.application'

# Time between two accesses from the same IP to qualify as a different view.
POST_VIEW_MINUTES = 7

COUNT_INTERVAL_WEEKS = 10000

# This flag is used flag situation where a data migration is in progress.
# Allows us to turn off certain type of actions (for example sending emails).
DATA_MIGRATION = False

# Tries to load up secret settings from a predetermined module
# This is for convenience only!
try:
    from conf.run.secrets import *
    print(f"Loaded secrets from: conf.run.secrets")
except Exception as exc:
    print(f"Secrets module not imported: {exc}")

