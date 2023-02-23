from dataclasses import dataclass

@dataclass
class Card:
    _id:str=None
    title:str=None
    image:str=None
    link:str=None
    episode:str=None
    episode_slang:str=None
    is_censored:bool=None
    