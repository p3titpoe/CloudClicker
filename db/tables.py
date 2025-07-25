import yail
from .sqlite_adapt import fetch_data,insert_data,update_data,col_defs,QueryObject



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
