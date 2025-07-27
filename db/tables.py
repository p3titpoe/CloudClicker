import yail
from enum import Enum
from .sqlite_adapt import fetch_data,raw_sql,insert_data,delete_data,update_data,col_defs,QueryObject

log = yail.get_logger('db-tables',public=True,handlers=['handler-file'])
yail.console_mute('db-tables')

##################################################################
#   Tables manip
##################################################################

def startdate_exists(startdate:str,tablename:str)->bool:
    qr = QueryObject(table=tablename,
                     search_column=["startdate"],
                     search_column_value=[startdate],
                     search_operator=['LIKE'])
    try:
        out = False
        res = fetch_data(qr)
        if len(res) > 0:
            out = True
        return out
    except:
        return False

def update_table(tablename:str,data:dict)->None:
    for uuid,evdata in data.items():
        found =  startdate_exists(evdata['startdate'],tablename)
        if not found:
            insert_data(tablename,evdata)
            log.info(f'Inserted {evdata["startdate"]} into {tablename}')

def get_uuid_dates(tablename:str)->dict:
    qr = QueryObject(tablename=tablename,
                     columns=['startdate','name'])
    res = fetch_data(qr)
    print(res)

def get_dbevent_by_date(dt:int,cal:str)->dict:
    qr = QueryObject(table=cal,
                     search_column='startdate',
                     search_column_value=str(dt))
    res = fetch_data(qr,True)
    return res[0]

def create_calendar_table(calendarname:str,ownerid:int)->None:
    name = f'{ownerid}-{calendarname}'
    sql = f"""CREATE TABLE "{name}" (
	"uuid"	TEXT,
	"startdate"	INTEGER UNIQUE,
	"name"	TEXT,
	"description"	TEXT,
	"location"	TEXT,
	PRIMARY KEY("startdate")
    )"""
    res = raw_sql(sql)
    print(res)

##################################################################
#   To Export
##################################################################
class TableManips(Enum):
    fetch = fetch_data
    raw = raw_sql
    insert = insert_data
    delete = delete_data
    update = update_data
    start_exists = startdate_exists
    event_by_date = get_dbevent_by_date
    new_cal_table = create_calendar_table