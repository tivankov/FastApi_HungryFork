from fastapi import FastAPI, HTTPException, Depends, Body
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
db = mongodb_client["hungry_fork"]
menu_collection = db["menu_items"]

app = FastAPI()

# Model za meni restorana
class MenuItem(BaseModel):
    name: str
    description: str
    price: float

class MenuItemDB(MenuItem):
    id: str

# Kreiranje stavki menija
@app.post("/menu/", response_model=MenuItemDB)
async def create_menu_item(item: MenuItem):
    item_db = MenuItemDB(**item.dict())
    result = await menu_collection.insert_one(item_db.dict())
    item_db.id = str(result.inserted_id)
    return item_db

# dohvacanje menija
@app.get("/menu/", response_model=List[MenuItemDB])
async def get_menu():
    menu_items = []
    async for item in menu_collection.find():
        item["_id"] = str(item["_id"])
        menu_items.append(MenuItemDB(**item))
    return menu_items

# dohvacanje stavki menija
@app.get("/menu/{item_id}", response_model=MenuItemDB)
async def get_menu_item(item_id: str):
    item = await menu_collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item["_id"] = str(item["_id"])
        return MenuItemDB(**item)
    else:
        raise HTTPException(status_code=404, detail="Menu item not found")

# brisanje stavki
@app.delete("/menu/{item_id}", response_model=MenuItemDB)
async def delete_menu_item(item_id: str):
    item = await menu_collection.find_one({"_id": ObjectId(item_id)})
    if item:
        await menu_collection.delete_one({"_id": ObjectId(item_id)})
        item["_id"] = str(item["_id"])
        return MenuItemDB(**item)
    else:
        raise HTTPException(status_code=404, detail="Menu item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
