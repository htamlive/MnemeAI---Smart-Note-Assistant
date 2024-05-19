# from pkg.model import Authz, ServiceType


# authorization = Authz.objects.filter(current_state="IWzZTo2F6FyrSagEQhRl7TkpzWxpQN", service_type=ServiceType.NOTION.value)
# if authorization:
#     authorization.update(
#         service_type=ServiceType.NOTION.value,
#         token="token",
#     )



from datetime import datetime, timedelta, timezone
import pytz


my_dict = {}

my_dict['inner_dict'] = {}


def do_somthing(cur_dict):
    cur_dict['key'] = 'value'

do_somthing(my_dict['inner_dict'])

inner_dict = my_dict['inner_dict']

inner_dict['key'] = 'value1'

# print(my_dict)


offset = 7*60

def update_tz(offset):
    return pytz.FixedOffset(offset)


tz = pytz.timezone('Etc/GMT-7')
# print(str(tz.tzname(datetime.now(tz))))
# print(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %A'))

due = "2022-10-10 17:42"

datetime.strptime(due, "%Y-%m-%d %H:%M").isoformat() + "Z"

