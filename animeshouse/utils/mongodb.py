from dotenv import load_dotenv
from pymongo import MongoClient
from typing import List, Dict
import re
import os

from . import check_is_same

load_dotenv()

class MongoDB():
    
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.media_database = self.client.get_database("blogdb")
        self.cache_doc = self.client.get_database("cache")
        self.animes_vision = self.media_database.get_collection("animes")
        self.cache = self.cache_doc.get_collection("home")
    
    def get_anime_by_title(self, title:str, _type:str="default") -> str|dict:
        # TODO: Verify the season number, not the nature season but the release
        search = list(self.animes_vision.find({"card.title": {"$regex": title, "$options": "i"}}))

        if len(search) == 0:
           search = list(self.animes_vision.find({"card.title": {"$regex": f"^{title}*", "$options": "i"}}))
           if len(search) == 0:
               title_ = title.replace(" - ", ".*", 1)
               search = list(self.animes_vision.find({"card.title": {"$regex": title_, "$options": "i"}}))
               if len(search) == 0:
                   search = list(self.animes_vision.find({"$text": {"$search": title}}))
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
    
    def get_all_by_title(self, title) -> Dict|None:
        search = list(self.animes_vision.find({"card.title": {"$regex": title, "$options": "i"}}))
        if len(search) > 0:
            return search
        
        return None
    
    def add_to_cache(self, obj:dict) -> str:
        # TODO: Verify if is existed
        try:
            # re.compile("Mix: Meisei Story.*Nidome no Natsu, Sora no Mukou e", re.IGNORECASE) 
            is_exists = list(self.cache.find({"link": obj.get("link")}))
            if len(is_exists) == 0:
                self.cache.insert_one(obj)
                return "Success!"
            return "This episode was registred before."
        except Exception as e:
            return str(e)