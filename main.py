from fastapi import FastAPI, Header,HTTPException
from pydantic import BaseModel
import sqlite3
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

#API_KEY auth
load_dotenv()
API_KEY=os.environ.get("API_KEY")


#sqllite makes db
conn = sqlite3.connect("tracker.db")
conn.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, category TEXT, value REAL)")
conn.commit()

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# defines the required shape of data for a new entry: category (text) + value (number)  
class Entries(BaseModel):
    category:str
    value:float

#saves data to db    receives a new entry, inserts it, 
@app.post("/entries")
async def entry(entry:Entries,x_api_key:str=Header(...)):
   if x_api_key !=API_KEY:
       raise HTTPException(status_code=401,detail="invalid api key")
   conn.execute("INSERT INTO entries (category, value) VALUES (?, ?)",(entry.category,entry.value))
   conn.commit()
   return{"status": "saved"}

# returns all current entries
@app.get("/entries")
async def query():
   return conn.execute("SELECT * FROM entries").fetchall()

#delelte function
@app.delete("/entries/{entry_id}")
async def delete(entry_id:int,x_api_key:str=Header(...)):
    if x_api_key !=API_KEY:
        raise HTTPException(status_code=401,detail="invalid api key")
    ac_del=conn.execute("DELETE FROM entries Where id = ?",(entry_id,))
    conn.commit()
    if ac_del.rowcount==0:
        return{'status':"entry_id not found"}
    return{"status":"deleted","id":entry_id}    

#fetch an entry
@app.get("/entries/{entry_id}")
async def fetch(entry_id:int):
    ac_select=conn.execute("SELECT * FROM entries WHERE id=?",(entry_id,))
    ac_fetch=ac_select.fetchone()
    if ac_fetch is None:
        return{"status":"entry not found"}
    return ac_fetch

#updating an entry
@app.put("/entries/{entry_id}")
async def update_entry(entry_id:int,entry:Entries,x_api_key:str=Header(...)):
    if x_api_key !=API_KEY:
        raise HTTPException(status_code=401,detail="invalid api key")
    ac_insert=conn.execute("UPDATE entries SET category = ?, value = ? WHERE id = ?",(entry.category,entry.value,entry_id))
    conn.commit()
    if ac_insert.rowcount==0:
        return{'status':'entry not updated '}
    return {'status':'updated entry','id':entry_id}

#showing the html ui
app.mount("/",StaticFiles(directory="static",html=True), name="static")