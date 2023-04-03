from dotenv import load_dotenv
from pymongo import MongoClient
from typing import List
import os

from . import check_is_same

load_dotenv()

class MongoDB():
    
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.media_database = self.client.get_database("blogdb")
        self.animes_vision = self.media_database.get_collection("animes")
    
    def get_anime_by_title(self, title:str, _type:str="default") -> str:
        search = list(self.animes_vision.find({"card.title": {"$regex": title, "$options": "i"}}))

        if len(search) == 0:
           search = list(self.animes_vision.find({"card.title": {"$regex": f"^{title}*", "$options": "i"}}))
           if len(search) == 0:
               return None
        
        if len(search) > 1:
            scores = [(check_is_same(title, i["card"]["title"][:-7]), idx) for idx, i in enumerate(search)]
            scores = sorted(scores, key=lambda x: x[0], reverse=True)
            
            if _type == "default":
                return search[scores[0][1]]["_id"]
            if _type == "complete":
                return search[scores[0][1]]
        
        if _type == "default":
            return search[0]["_id"]
        
        if _type == "complete":
            return search[0]
    
    