import requests
from dataclasses import dataclass
from json import dumps,loads
from enum import Enum
from textwrap import dedent
from datetime import datetime,timedelta
from uuid import uuid1
from ics import Calendar


class RegExDefs(Enum):
    EVENT = r"'([a-zA-Z0-9/.?@=+ &\-_]+)'"
    DATE = r'(\d+/\d+/\d+)'
    SUMMARY_LOC=r'\([^()]+\)'
    CAL_STARTDATE = r"DTSTART;TZID=Europe/Oslo:([0-9].)"

class DTFormats(Enum):
    DATE_EVENT = '%Y%m%d'
    DATE_FROM_MAIL = '%d/%m/%Y'
    DATE_FULL = '%Y%m%dT%H%M%SZ'
    DATE_NORMAL = '%Y-%m-%d'

@dataclass
class DbEvent:
    uuid:str
    startdate:int
    name:str
    description:str

@dataclass
class CalEvent:
    _UID:uuid1 = None
    _CREATED:str =""
    _DTSTAMP:str =""
    _TZID:str = "Europe/Luxembourg"
    _DTSTART:datetime = ""
    _DTEND:datetime = ""
    _LOCATION: str = ""
    SUMMARY:str = ""
    DESCRIPTION:str = "IN: | OUT: | Total:"
    @property
    def uuid(self):
        return self._UID

    @property
    def start_time(self):
        return self._DTSTART

    @start_time.setter
    def start_time(self, value:str):
        start = datetime.strptime(value,'%Y%m%d')
        self._DTSTART = start

    def from_db(self,data:dict)->None:
        trans = {'startdate':self._DTSTART,
                 'name':self.SUMMARY,
                 'uuid':self._UID,
                 'description':self.DESCRIPTION,
                 'location':self._LOCATION}
        for k,v in data.items():
            if k == "startdate":
                trans[k] = datetime.strptime(v,'%Y%m%d')
            elif k == "description":
                trans[k] += f"\n {v}"
            else:
                trans[k] = v


    def format_datetime(self, dt, mode:int = 0):
        fmts = ['%Y%m%dT%H%M%SZ','%Y%m%d']
        return dt.strftime(fmts[mode])

    def make_uuid(self)->str:
        out = ""
        if self._UID is None:
            self._UID = uuid1()
            out = self._UID
        return out

    def create_event_data(self):
        self.make_uuid()
        self._CREATED = self.format_datetime(datetime.now())
        self._DTSTAMP = self.format_datetime(datetime.now())
        startd = self._DTSTART
        endd = startd + timedelta(days=1)
        self._DTSTART = self.format_datetime(startd,1)
        self._DTEND = self.format_datetime(endd,1)


        event_data = dedent(f"""BEGIN:VCALENDAR
        PRODID:-//IDN nextcloud.com//Calendar app 5.2.2//EN
        CALSCALE:GREGORIAN
        VERSION:2.0
        BEGIN:VEVENT
        UID:{self._UID}
        CREATED:{self._CREATED}
        DTSTAMP:{self._DTSTAMP}
        LAST-MODIFIED:{self._CREATED}
        SEQUENCE:2
        DTSTART;VALUE=DATE:{self._DTSTART}
        DTEND;VALUE=DATE:{self._DTEND}
        SUMMARY:{self.SUMMARY}
        DESCRIPTION:{self.DESCRIPTION}
        LOCATION:{self._LOCATION}
        END:VEVENT
        END:VCALENDAR
        """).strip()
        return event_data

@dataclass
class FetchedEmail:
    id:int = 0
    subject:str = ""
    _sender:str = ""
    startdate:int = 0
    msg:str = ""

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value:str):
        splitted = value.split("<")[1]
        self._sender = splitted[:-1]

    def from_save(self,jsoned:str)->None:
        data = loads(jsoned)
        kyz = [k for k in self.__dict__.keys() if k[1] != "_"]
        for k,v in data.items():
            if k in kyz:
                # attr = "_"+k if k != "sender" else k
                self.__dict__[k] = v

    def from_db(self,data:dict):
        # print(data)
        kyz = [k for k in self.__dict__.keys() if k[1] != "_"]
        for k, v in data.items():
            if k in kyz:
                # attr = "_"+k if k != "sender" else k
                self.__dict__[k] = v
        self.__dict__['_sender'] = data['sender']

    def to_db(self)->dict:
        out = {"id": self.id,
               "subject": self.subject,
               "startdate": self.startdate,
               "sender": self.sender,
               "msg": self.msg,
               }
        return out

    def save(self)->str:
            out = self.to_db()
            return dumps(out)
