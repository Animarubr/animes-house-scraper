from difflib import SequenceMatcher
import jsbeautifier
import base64

BASE_ROOT = "https://animeshouse.net/"

NEWS_EPISODES = "https://animeshouse.net/episodio/page/{}/"
    #--> {1} Page nuber
    
ANIME_PAGE = "https://animeshouse.net/anime/{}/"
    #--> {ningen-fushin-no-boukensha-tachi-ga-sekai-wo-sukuu-you-desu} Slang of serie name

EPISODE_VIDEO_PAGE = "https://animeshouse.net/episodio/{}/" 
    #--> {ningen-fushin-no-boukensha-tachi-ga-sekai-wo-sukuu-you-desu} => Slang of serie name, ease to handle
    #--> {s1} => Season of serie
    #--> {episodio-9} Slang if episode
    #--> {legendado-hd} Slang of the Type of audio and media quality Default HD
MOVIE_VIDEO_PAGE = "https://animeshouse.net/filme/{}/"

VIDEO_IFRAME_BUILDER = "https://animeshouse.net/wp-admin/admin-ajax.php"
"""
    Recive the following parameters:
        {
            action: 'doo_player_ajax',
            post: int, -> post number, it's something like an id for the blog post
            nume: int, -> player option
            type: str -> media from, ex.: tv, filme, ova
        }
"""
SEARCH_ENDPOINT = "https://animeshouse.net/?s={}"

EXTERNAL_VIDEO_PAGE = "https://linkshort.fun/"
# Recive one hashed parameter to access player page 

def check_is_same(search:str, db_title:str):

    if "2" in search:
        print("* ",db_title)
    return SequenceMatcher(None, search, db_title).ratio()

def parse_episode(text:str) -> tuple|None:
    """extract numbers of string and creation of episode slang"""
    if text != "":
        slang = text.replace(" ", "-").strip().lower()
        episode = [float(s) for s in text.split() if s.isdigit()]
        is_censored = False if "censura" in slang else True
        return (slang, episode, is_censored)
    
    return None

def parse_bytes(data:str) -> str:
    parsed_bytes = data.split("<script>document.write(atob(")[1].split("));</script>")[0].replace('"', '').encode('utf-8').decode('unicode_escape')        
    decodedBytes = base64.b64decode(parsed_bytes)
    decodedStr = str(decodedBytes, "utf-8")
    return decodedBytes

def deoffuscator(offuscated_function:str) -> str:
    return jsbeautifier.beautify(offuscated_function)