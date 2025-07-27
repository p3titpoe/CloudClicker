import yail
from ics import Calendar
import requests
from db import Config, ConfigSetting
from db.tables import update_table, get_uuid_dates, QueryObject, fetch_data
from .caldav_lib import get_connection,close_connection,calendar_from_dav,DavCals
# from .cresacat_dummy_model import dummy
from enum import Enum

cf = Config.setting_by_name('crescat')
url = cf.value
log = yail.logger_by_name('main')

##################################################################
#   Calendar manips
##################################################################

def calendar_from_link(config:ConfigSetting)->dict:
    # cal = Calendar(dummy)
    cal = Calendar(requests.get(config.value).text)
    out= {}
    to_sort = {}
    for x in cal.events:
        uuid = x.uid
        # print(uuid)
        startdate = x.begin.strftime("%Y%m%d")
        to_sort[startdate] = uuid
        tmp ={'uuid':uuid,'startdate':startdate,'name':x.name,'description':str(x.description),'location':x.location}
        out[uuid] = tmp
    sorted_out = sorted(to_sort,reverse=True)
    log.log(f'Fetched {len(sorted_out)} from {cf.name}')
    return {to_sort[k]:out[to_sort[k]] for k in sorted_out}


def calendar_update(config:ConfigSetting,events:list):
    nxtd = get_connection(config=config)
    nxtdcal = DavCals(nxtd)
    for m in events:
        nxtdcal.add_event(summary=m['name'],start_time=m['startdate'])

##################################################################
#   Tables manip
##################################################################


def update_tables(table:str = None):
    func = {'link':calendar_from_link,
            'dav':calendar_from_dav}
    print(f'Updating {table}')
    data:dict = func[table]()
    # uuids_in_db = get_uuid_dates(t)
    # uuids_in_fetch = [k for k in data.keys()]
    # entries_to_del = [k for k in uuids_in_db.keys() if k not in uuids_in_fetch]
    update_table(table,data)

##################################################################
#   To Export
##################################################################

class CalendarManips(Enum):
    from_dav = calendar_from_dav
    from_link = calendar_from_link
    update = calendar_update
    get_dav = get_connection
    close_dav = close_connection


# print(requests.get(url).text)