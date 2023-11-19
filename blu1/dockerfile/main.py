import asyncio
import pymongo


import faust
import asyncpg



app = faust.App(
    'blu',
    broker='kafka://kafka:9092',
)

async def run_query(query,read:bool):
    conn=await asyncpg.connect(host='postgres',port=5432,user='postgres',password='postgres',database='blu')
    if read:
       row=await conn.fetchrow(query)
       return row
    else:
       execute=await conn.execute(query)
       return execute



class Event(faust.Record):
    #     id: int
    #     client_id: int
    #     type: int
    #     account_no: int
    #     is_active: bool
    #     creation_date: str
    #     last_modification_date: str
    before: dict
    after: dict
    op: str
    source: dict

async def create_mongo_record(event:Event)-> dict:
    credit=event.after['credit']
    record=dict()
    record['id']=event.after['id']
    record['amount']=event.after['amount']
    record['transaction_date']=event.after['transaction_date']

    transaction_type_id=event.after['type']
    type_name_query=f"select name from task.transaction_type where id={event.after['type']}"
    type_name=await run_query(type_name_query,True)
    record['type_name']=type_name['name']

    to_account_id=event.after['to_account_id']
    from_account_id=event.after['from_account_id']

    to_account_query=f'select account_no,client_id,type from task.account where id={to_account_id}'
    from_account_query=f'select account_no,client_id,type from task.account where id={from_account_id}'
    to_account=await run_query(to_account_query,True)
    from_account=await run_query(from_account_query,True)

    to_account_customer_name_query=f"select name,type from task.customer where id={to_account['client_id']}"
    from_account_customer_name_query=f"select name,type from task.customer where id={from_account['client_id']}"
    to_customer_name=await run_query(to_account_customer_name_query,True)
    from_customer_name=await run_query(from_account_customer_name_query,True)

    if credit:
        first_person_account=to_account
        second_person_account=from_account
        first_person_customer=to_customer_name
        second_person_customer=from_customer_name
    else:
        first_person_account = from_account
        second_person_account = to_account
        first_person_customer = from_customer_name
        second_person_customer = to_customer_name

    record['account_number']=first_person_account['account_no']
    record['customer_name']=first_person_customer['name']
    record['destination_account_number']=second_person_account['account_no']
    record['destination_customer_name']=second_person_customer['name']

    account_type_query=f"select name from task.account_types where id={second_person_account['type']}"
    account_type_name=await run_query(account_type_query,True)
    record['destination_account_type_name']=account_type_name['name']

    record['credit']=credit

    customer_type_query=f"select name from task.customer_type where id={second_person_customer['type']}"
    customer_type=await run_query(customer_type_query,True)
    record['is_Juridical']=customer_type['name']

    return record


async def insert_mongo(record:dict):
    myclient = pymongo.MongoClient("mongodb://root:root@mongodb_container:27017/")
    mydb = myclient["blu"]
    mycol = mydb["Transaction"]
    x = mycol.insert_one(record)
    return x



blu_task_account_topic = app.topic('blu.task.transaction', value_type=Event)


@app.agent(blu_task_account_topic)
async def mytask(stream):
    async for w in stream:
        #events captured in snapshot
        if (w.op=='r' and w.source['snapshot']!='fasle') or (w.op=='c'):
           record=await create_mongo_record(w)
           await insert_mongo(record)



if __name__ == '__main__':
    app.main()
    
    
    
    
    
