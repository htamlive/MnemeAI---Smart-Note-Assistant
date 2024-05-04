import django
from django.conf import settings

from config import config

def setup_django_orm():
    settings.configure( 
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config.DB_NAME,
                'USER': config.DB_USER,
                'PASSWORD': config.DB_PASS,
                'HOST': config.DB_HOST,
                'PORT': config.DB_PORT,
            }
        },
        INSTALLED_APPS = [
            'pkg',
        ]
    )

    django.setup()