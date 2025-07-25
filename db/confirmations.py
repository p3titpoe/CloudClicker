from .sqlite_adapt import fetch_data,insert_data,update_data,col_defs,QueryObject

def mail_exists(given_id:int)->bool:
    qr = QueryObject(table='confirmations',
                     search_column='id',
                     )
    try:
        res = fetch_data(qr)
        return True
    except:
        return False

def get_mail(realid:int)->dict:
    qry = QueryObject(table='confirmations',
                      search_column='rid',
                      search_column_value=str(realid))
    try:
        res = fetch_data(qry,True)[0]
        return res
    except:
        return {}

def get_last_mail()->list:
    qr=QueryObject(table='confirmations',
                   order_by='rid',
                   order_mode='DESC')
    res = fetch_data(qry=qr,to_dict=True)[0:2]
    return res

def insert_new_mail(data):
    if not mail_exists(data['given_id']):
        insert_data('confirmations',data)

def get_subjects_list()->list:
    qr = QueryObject(table='confirmations',
                     columns=['subject'])
    res = fetch_data(qr)
    out = [p[0] for p in res]
    # print(out)
    return out

def startdate_list()->list:
    qr = QueryObject(table='confirmations',
                     columns=['startdate'])

    res = fetch_data(qr)
    out = [p[0] for p in res]
    # print(out)
    return out