from dataclasses import dataclass, asdict
from typing import List
import json


class Meta:
    
    @property
    def to_json(self):
        return json.dumps(asdict(self), indent=4, ensure_ascii=False)


@dataclass
class Card(Meta):
    _id:str=None
    title:str=None
    image:str=None
    link:str=None
    episode:str=None
    episode_slang:str=None
    is_censored:bool=None
    

@dataclass
class Season(Meta):
    _id:str=None
    season_number:int=None
    episodes:List[str]=None
    
    
@dataclass
class Anime(Meta):
    _id:str=None
    title:str=None
    image:str=None
    genres:str=None
    seasons:Season()=None
    
@dataclass
class Stream(Meta):
    quality:str=None
    stream:str=None
    

@dataclass
class Video(Meta):
    _id:str=None
    option:int=None
    streams:List[Stream]=None
    