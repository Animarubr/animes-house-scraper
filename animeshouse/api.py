from selectolax.parser import HTMLParser
from typing import List

from .session import Session
from .utils import parse_episode, NEWS_EPISODES, EPISODE_VIDEO_PAGE
from .types import Card, Video
from .utils.mongodb import MongoDB

class AnimesHouse(Session):
    
    def __init__(self):
        super().__init__()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        self.database = MongoDB()
    
    def parse(self, body:str):
        return HTMLParser(body)
    
    def get_news_episodes_by_page(self, page:int) -> List[Card]|None:
        """TODO: Correlacionar com animes no mongodb ou adicionar como novo anime"""
        request_news_episodes =  self._make_request(method="GET", url=NEWS_EPISODES.format(page), headers=self.headers)
        html = self.parse(request_news_episodes.text)
        
        imgs = [img.css_first("img").attrs["src"] for img in html.css("div.poster")]
        titles = [title.css_first("h3").text() for title in html.css("article.episodes")]
        links = [title.css_first("h3").css_first("a").attrs["href"] for title in html.css("article.episodes")]
        slangs, episodes, is_censored = zip(*[parse_episode(title.css_first("div.data").css_first("div.epi").text()) for title in html.css("article.episodes")])
        
        if (len(imgs) == len(titles) == len(links) == len(slangs) == len(episodes) == len(is_censored)):
            response = []
            for index, i in enumerate(imgs):
                card = Card(
                    _id=self.database.get_anime_by_title(titles[index]),
                    title=titles[index],
                    image=i,
                    link=links[index],
                    episode=episodes[index],
                    episode_slang=slangs[index],
                    is_censored=is_censored[index]
                )
                response.append(card)
            
            return response
        return None
    
    def get_video_streams(self, url:str) -> List[Video]|None:
        request_news_episodes =  self._make_request(method="GET", url=EPISODE_VIDEO_PAGE.format(), headers=self.headers)
        html = self.parse(request_news_episodes.text)
        pass
    
    