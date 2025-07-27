import yail
from caldav import DAVClient,Principal, Calendar
from dataclasses import dataclass
from db import Config, ConfigSetting
from .objs import CalEvent


log = yail.get_logger('caldav',public=True,handlers=['handler-file'])
yail.console_mute('caldav')
##################################################################
#   Classes
###################################################################

@dataclass
class DavConnect:
    _config:ConfigSetting
    client:DAVClient = None
    def_calendar:str = None
    principal:Principal = None


    @property
    def config_name(self)->str:
        return self._config.name

    def connect(self,verify_ssl:bool=True)->None:
        try:
            cf = Config.setting_by_name(self.config_name)
            url, username, password, default_cal = self._config.to_list()
            self.def_calendar = default_cal
            self.client = DAVClient(url, username=username, password=password, ssl_verify_cert=verify_ssl)
            self.principal = self.client.principal()
            log.log('DAV connection established')

        except Exception as e:
            log.error('DAV connection problem:',loggger_msg_data=e)
            print(f"Error initializing client: {e}")
            self.principal = None

    def close(self):
        log.log('DAV connection closed')
        self.client.close()

@dataclass
class DavConLibrary:
    lib: dict[str:DavConnect] = None

    def __del__(self):
        for k,v in self.lib.items():
            v.close()

    def __post_init__(self):
        self.lib = {}

    def add_con(self, name:str,con: DavConnect) -> None:
        if name not in self.lib:
            self.lib[name] = con

    def get_con(self, con_name: str) -> DavConnect:
        return self.lib[con_name]

    def del_con(self, con_name: str):
        del self.lib[con_name]


@dataclass
class DavCals:
    client:DavConnect
    _default_calendar:str = ""

    def __post_init__(self):
        self.default_calendar = self.client.def_calendar

    def _set_calendar(self,calendar_name:str):
        cal = calendar_name
        if calendar_name is None:
            cal = self._default_calendar
        return cal

    def by_name(self, calendar_name:str=None)->Calendar:
        calendar_name = self._set_calendar(calendar_name)
        try:
            calendars = self.client.principal.calendars()
            for calendar in calendars:
                if calendar.name == calendar_name:
                    return calendar
        except Exception as e:
            print(f"Error retrieving calendar: {e}")
        return None

    def calendars(self)->list:
        cals = [calendar.name for calendar in self.client.principal.calendars()]
        return cals

    def events(self, calendar_name:str=None):
        calendar_name = self._set_calendar(calendar_name)
        try:
            calendar = self.by_name(calendar_name)
            if not calendar:
                log.error(f'Calendar {calendar_name} not found')
                print(f'Calendar {calendar_name} not found')
                return False

            event_list = []
            for event in calendar.events():
                # event_list.append(Calendar.from_ical(event.data))
                event_list.append(event.data)
            log.log(f'Retrieved {len(event_list)} from {calendar_name}')
            return event_list

        except Exception as e:
            log.error(f'Calendar {calendar_name} not found')
            print(f"Error retrieving events: {e}")
            return False

    def update_event(self,uuid:str,data:dict,calendar_name:str = None):
        calendar_name = self._set_calendar(calendar_name)
        cal = self.by_name(calendar_name)
        ev = cal.event_by_uid(uuid)
        kyz = [c for c in ev.component.keys()]
        for k,v in data.items():
            if k.upper() in kyz:
                ev.component[k.upper()] = v
        print(ev.component)

    def add_event(self, start_time, summary, calendar_name:str=None):
        calendar_name = self._set_calendar(calendar_name)
        evt = CalEvent()
        evt.start_time = start_time
        evt.SUMMARY = summary
        try:
            calendar = self.by_name(calendar_name)
            if calendar:
                event_data = evt.create_event_data()
                # print(event_data)
                calendar.add_event(event_data)
                log.log(f'Inserted {summary} into {calendar_name}')
                return f"Event added to {calendar_name}"
            return "Calendar not found"
        except Exception as e:
            print(f"Error adding event: {e}")
            return False


##################################################################
#   Funcs to be exposed
##################################################################


lib = {}
def new_connection(config:ConfigSetting,verify:bool=True)->DavConnect:
    con = DavConnect(config)
    con.connect(verify_ssl= verify)
    lib[config.name] = con
    log.log(f"Connection for config {config.name} created")
    return con

def get_connection(config:ConfigSetting)->DavConnect:
    out = None
    if config.name in lib:
        out = lib[config.name]
    else:
        out = new_connection(config)
    return out

def close_connection(config_name:str)->None:
    del lib[config_name]

def calendar_from_dav(config:ConfigSetting)->dict:
    dclient = get_connection(config)
    calendars = DavCals(dclient)
    jp_cal = calendars.by_name()
    # print(jp_cal)
    out = {}
    to_sort = {}
    events = jp_cal.events()
    hh = True
    for e in events:
        kys = e.component.keys()
        startdate = e.component['DTSTART'].dt.strftime('%Y%m%d')
        name = str(e.component['SUMMARY'])
        descr = ""
        if "DESCRIPTION" in kys:
            descr = str(e.component['DESCRIPTION'])
        location = ""
        if "LOCATION" in kys:
            location = str(e.component['LOCATION'])
        uid = str(e.component['UID'])
        to_sort[startdate] = uid
        tmp ={'uuid':uid,'startdate':startdate,'name':name,'description':descr, 'location':location}
        out[uid] = tmp
    sorted_d = sorted(to_sort,reverse=True)
    close_connection(config.name)
    log.log(f'Fetched {len(sorted_d)} from {config.name}')

    return {to_sort[k]:out[to_sort[k]] for k in sorted_d}
