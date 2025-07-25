import sqlite3
import os
from .logic import QueryObject
from dataclasses import dataclass

BASEDIR = os.path.dirname(os.path.abspath(__file__))
dbloc = f'{BASEDIR}/main.db'



@dataclass(init=False)
class SqlAdapter:
    db_loc:str #path to db
    db_b:any
    db_c:any

    def __init__(self,loc:str)->None:
        self.db_loc = loc
        self.db_b = sqlite3.connect(self.db_loc, isolation_level=None)
        self.db_c = self.db_b.cursor()
        self._trans_list: dict = {'TEXT': str, 'INTEGER':int}


ADAPTER = SqlAdapter(dbloc)

def fetch_data(qry: QueryObject, to_dict=False)->list:
    sql = qry.query
    ptr = ADAPTER.db_c.execute(sql)
    tmp = ptr.fetchall()
    res = tmp
    if to_dict:
        res = []
        cols = qry.columns
        if cols == None:
            cols = [n['label'] for n in col_defs(qry.table)]
        for row in tmp:
            tmp_d = {}
            for i,v in enumerate(row):
                lab = cols[i]
                tmp_d[lab] = v
            res.append(tmp_d)
    return res

def insert_data(table,key_vals:dict)->list:
    ins_txt = f"INSERT INTO {table} ("
    val_txt = f"VALUES("
    for k, v in key_vals.items():
        if k is not None and v is not None:
            ins = f"'{k}',"
            ins_txt += ins
            if type(v) == str:
                v = v.replace('"',"'")
                val_txt += f'"{v}",'
            else:
                val_txt += f"{v},"
    ins = ins_txt[:-1] + ")"
    val = val_txt[:-1] + ")"
    sql = ins + " " + val
    # print(sql)
    ptr = ADAPTER.db_c.execute(sql)
    res = ptr.fetchall()
    return res

def update_data(table: str, kvals: dict, checkcol = "id"):
    """
    Updates sets in database

    PARAMETERS:
        - table: str = name of the table
        - kvals: dict = dict containing the insert data in key(column name) - value
        - checkcol: str = column to check against, default = id

    RETURNS:
       -  None

    """
    txt=f"UPDATE {table} SET "
    vals=[]

    for k,v in kvals.items():
        if k != checkcol:
            tt="{} = ".format(k)
            txt +=tt
            vt="{} ,"
            if type(v)==str:
               txt +=f"'{v}',"
            else:
                txt += f"{v},"
    end='WHERE {}.{} = {}'.format(table,checkcol,kvals[checkcol])
    sql= txt[:-1]+" "+end
    res =ADAPTER.db_c.execute(sql)

def delete_data(table:str, id:int)->None:
    ptr = ADAPTER.db_c
    sql = f"DELETE FROM {table} WHERE id = ?"
    res = ptr.execute(sql,[id])
    return res

def col_defs(table:str)->list:
    sql = f"PRAGMA table_info({table})"
    ptr = ADAPTER.db_c.execute(sql)
    tmp = ptr.fetchall()
    res = [{'label':x[1],'type':ADAPTER._trans_list[x[2]]} for x in tmp]
    return res

def create_calendar_table(calendarname:str,ownerid:int)->None:
    ptr = ADAPTER.db_c
    name = f'{ownerid}-{calendarname}'
    sql = """CREATE TABLE "crescat" (
	"uuid"	TEXT,
	"startdate"	INTEGER UNIQUE,
	"name"	TEXT,
	"description"	TEXT,
	"location"	TEXT,
	PRIMARY KEY("startdate")
    )"""
    res = ptr.execute(sql)
    print(res)