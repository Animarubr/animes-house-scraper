from selectolax.parser import HTMLParser
from typing import List

from .session import Session
from .utils import parse_episode,BASE_ROOT, NEWS_EPISODES, EPISODE_VIDEO_PAGE, VIDEO_IFRAME_BUILDER
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
        request_news_episodes = self._make_request(method="GET", url=NEWS_EPISODES.format(page), headers=self.headers)
        html = self.parse(request_news_episodes.text)
        
        imgs = [img.css_first("img").attrs["src"] for img in html.css("div.poster")]
        titles = [title.css_first("h3").text() for title in html.css("article.episodes")]
        links = [title.css_first("h3").css_first("a").attrs["href"].split("/")[4] for title in html.css("article.episodes")]
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
    
    def get_videos_external_links(self, slang_episode:str) -> List[Video]|None:
        # TODO: Create loop to get external links for all players otions
        request_news_episodes = self._make_request(method="GET", url=EPISODE_VIDEO_PAGE.format(slang_episode), headers=self.headers)
        html = self.parse(request_news_episodes.text)
        players_attrs = [(e.attributes.get("data-type"), e.attributes.get("data-post"), e.attributes.get("data-nume")) for e in html.css("li.dooplay_player_option")]
        
        payload = {
            "action": "doo_player_ajax",
            "post": players_attrs[0][1],
            "nume": players_attrs[0][2],
            "type": players_attrs[0][0]
        }
        headers = self.headers
        headers["content-type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["origin"] = BASE_ROOT
        headers["referer"] = EPISODE_VIDEO_PAGE.format(slang_episode)
        
        request_ajax = self._make_request(method="POST", url=VIDEO_IFRAME_BUILDER, data=payload, headers=headers)
        iframe_parse = self.parse(request_ajax.text)
        base_iframe_uri = iframe_parse.css_first("iframe").attrs["src"]
        
        request_iframe = self._make_request(method="GET", url=f"{BASE_ROOT}{base_iframe_uri}", headers=self.headers)
        external_link_parse = self.parse(request_iframe.text)

        response = external_link_parse.css_first("a").attrs["href"]
        
        return response

