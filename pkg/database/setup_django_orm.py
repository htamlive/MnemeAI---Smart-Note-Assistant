import django
from django.conf import settings

import os

def setup_django_orm():
    print("Setting up Django ORM")
    settings.configure( 
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv("DATABASE_NAME"),
                'USER': os.getenv("DATABASE_USER"),
                'PASSWORD': os.getenv("DATABASE_PASSWORD"),
                'HOST': os.getenv("DATABASE_HOST"),
                'PORT': os.getenv("DATABASE_PORT"),
            }
        },
        INSTALLED_APPS = [
            'pkg',
        ]
    )

    print("DATABASE_NAME: ", os.getenv("DATABASE_NAME"))

    django.setup()