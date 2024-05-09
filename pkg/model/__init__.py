from .setup_django_orm import setup_django_orm
setup_django_orm()

__all__=[
    'Authz',
    'ServiceType',
    'ReminderCeleryTask'
]

from .authz import Authz, ServiceType
from .reminder_cele_task import ReminderCeleryTask