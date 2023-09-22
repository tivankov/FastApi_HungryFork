import database
import models
import security
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List
from pymongo import MongoClient
from bson import ObjectId


app = FastAPI()

# Spajanje na mongo bazu podataka
client = MongoClient("mongodb://localhost:27017/")
db = client["hungry_fork"]
collection = db["menu_items"]

# Model za stavke menija
class MenuItemIn(models.BaseModel):
    name: str
    description: str
    price: float

class MenuItemDb(MenuItemIn):
    id: str

# API rute do menija
@app.post("/menu/", response_model=MenuItemDb)
async def create_menu_item(menu_item_in: MenuItemIn):
    new_menu_item = MenuItemDb(**menu_item_in.dict())
    result = collection.insert_one(new_menu_item.dict())
    new_menu_item.id = str(result.inserted_id)
    return new_menu_item

@app.get("/menu/", response_model=List[MenuItemDb])
async def read_menu():
    menu_items = list(collection.find())
    return menu_items

@app.get("/menu/{item_id}", response_model=MenuItemDb)
async def read_menu_item(item_id: str):
    menu_item = collection.find_one({"_id": ObjectId(item_id)})
    if menu_item:
        return MenuItemDb(**menu_item)
    else:
        raise HTTPException(status_code=404, detail="Menu item not found")

@app.delete("/menu/{item_id}", response_model=MenuItemDb)
async def delete_menu_item(item_id: str):
    menu_item = collection.find_one({"_id": ObjectId(item_id)})
    if menu_item:
        collection.delete_one({"_id": ObjectId(item_id)})
        return MenuItemDb(**menu_item)
    else:
        raise HTTPException(status_code=404, detail="Menu item not found")
