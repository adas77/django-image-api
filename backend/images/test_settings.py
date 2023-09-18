import os
from .dev_settings import *

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "mediafiles/test")
