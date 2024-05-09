from pkg.model import Authz, ServiceType


authorization = Authz.objects.filter(current_state="IWzZTo2F6FyrSagEQhRl7TkpzWxpQN", service_type=ServiceType.NOTION.value)
if authorization:
    authorization.update(
        service_type=ServiceType.NOTION.value,
        token="token",
    )