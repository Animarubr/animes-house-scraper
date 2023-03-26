from difflib import SequenceMatcher
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

def check_is_same(search:str, db_title:str):
    return SequenceMatcher(None, search, db_title).ratio()

def parse_episode(text:str) -> tuple|None:
    """Retirar números da string e criar slang da string"""
    if text != "":
        slang = text.replace(" ", "-").strip().lower()
        episode = [float(s) for s in text.split() if s.isdigit()]
        is_censored = False if "censura" in slang else True
        return (slang, episode, is_censored)
    
    return None