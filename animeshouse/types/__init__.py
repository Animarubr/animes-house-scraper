from dataclasses import dataclass
from typing import List
from json import dumps

class Meta(type, metaclass=type("", (type,), {"__str__": lambda _: "~hi"})):
    def __str__(self):
        return f"<class 'animes_house.types.{self.__name__}'>"

class Object(metaclass=Meta):
    @staticmethod
    def default(obj: "Object"):
        return {
            "_": obj.__class__.__name__,
            **{
                attr: (
                    "*" * 5
                    if attr in ("access_token", "refresh_token")
                    else getattr(obj, attr)
                )
                for attr in filter(lambda x: not x.startswith("_"), obj.__dict__)
                if getattr(obj, attr) is not None
            }
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=Object.default, ensure_ascii=False)


@dataclass
class Card:
    _id:str=None
    title:str=None
    image:str=None
    link:str=None
    episode:str=None
    episode_slang:str=None
    is_censored:bool=None

@dataclass
class Season:
    _id:str
    season_number:int
    episodes:List[str]

@dataclass
class Anime:
    _id:str
    title:str
    image:str
    genres:str
    seasons: Season()