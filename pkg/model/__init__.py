from .setup_django_orm import setup_django_orm
setup_django_orm()

__all__=[
    'Authz',
    'ServiceType',
]

from .authz import Authz, ServiceType