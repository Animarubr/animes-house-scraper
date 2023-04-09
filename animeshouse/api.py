from selectolax.parser import HTMLParser
from urllib.parse import unquote
from typing import List, Dict
from datetime import datetime
import demjson

from .session import Session
from .utils import parse_episode, parse_bytes, deoffuscator, BASE_ROOT, NEWS_EPISODES, EPISODE_VIDEO_PAGE, VIDEO_IFRAME_BUILDER, EXTERNAL_VIDEO_PAGE, ANIME_PAGE
from .types import Card, Video, Episodes
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
                _id = self.database.get_anime_by_title(titles[index])
                if _id is None:
                    print(titles[index])
                # card = Card(
                #     anime_id=_id,
                #     title=titles[index],
                #     image=i,
                #     link=links[index],
                #     episode=episodes[index],
                #     episode_slang=slangs[index],
                #     is_censored=is_censored[index],
                #     created_at=str(datetime.utcnow())
                # )
                # add_to_cache = self.database.add_to_cache(card.__dict__)
                # if "Success!" in add_to_cache:
                #     response.append(card)
                # else:
                #     print(add_to_cache)
                #     break
            
            return response
        return None
    
    def get_videos_external_links(self, slang_episode:str) -> List[Video]|None:
 
        request_news_episodes = self._make_request(method="GET", url=EPISODE_VIDEO_PAGE.format(slang_episode), headers=self.headers)
        html = self.parse(request_news_episodes.text)
        players_attrs = [(e.attributes.get("data-type"), e.attributes.get("data-post"), e.attributes.get("data-nume")) for e in html.css("li.dooplay_player_option")]
        
        response = []
        
        for i in players_attrs:
        
            payload = {
                "action": "doo_player_ajax",
                "post": i[1],
                "nume": i[2],
                "type": i[0]
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

            response.append(external_link_parse.css_first("a").attrs["href"])
        
        streams = [self._get_streams(e, EPISODE_VIDEO_PAGE.format(slang_episode)) for e in response]
        return streams
    
    def _get_streams(self, external_link:str, slang_episode:str) -> Video|None:
        #TODO: Needs to refatoration
        
        self.headers["referer"] = EPISODE_VIDEO_PAGE.format(slang_episode)
        request_external = self._make_request("GET", url=external_link, headers=self.headers)
        
        decodedStr = parse_bytes(request_external.text)
        external_parsed = self.parse(decodedStr)
        
        action = external_parsed.css_first("form#nunca_se_endireita").attrs["action"]
        inputs = {e.attributes.get("name"): e.attributes.get("value") for e in external_parsed.css("input")}
        
        headers = self.headers
        headers["content-type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["origin"] = EXTERNAL_VIDEO_PAGE
        headers["referer"] = external_link
        
        request_video_page = self._make_request("POST", url=action, data=inputs, headers=headers)
        decodedStr_v2 = parse_bytes(request_video_page.text)
        external_parsed_v2 = self.parse(decodedStr_v2)

        action_v2 = external_parsed_v2.css_first("form").attrs["action"]
        inputs_v2 = {e.attributes.get("name"): e.attributes.get("value") for e in external_parsed_v2.css("input")}
        headers["referer"] = action
        
        request_video_page_v2 = self._make_request("POST", url=action_v2, data=inputs_v2, headers=headers)
        decodedStr_v3 = parse_bytes(request_video_page_v2.text)
        external_parsed_v3 = self.parse(decodedStr_v3)
        
        action_v3 = external_parsed_v3.css_first("form").attrs["action"]
        inputs_v3 = {e.attributes.get("name"): e.attributes.get("value") for e in external_parsed_v3.css("input")}
        
        headers["origin"] = EXTERNAL_VIDEO_PAGE
        headers["referer"] = EXTERNAL_VIDEO_PAGE
        
        request_video_page_v3 = self._make_request("POST", url=action_v3, data=inputs_v3, headers=headers)
        main_html = self.parse(parse_bytes(request_video_page_v3.text))
        main_attrs = [i.attributes for i in main_html.css("iframe")]
        if main_attrs != []:
            del headers["origin"]
            del headers["referer"]
            
            headers["accept-language"] = "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
            action_v4 = unquote(main_attrs[0].get("src"))
            final_request = self._make_request("GET", url=action_v4, headers=headers)
            
            parsed_final = self.parse(final_request.text)
            offuscated_function = [e.text() for e in parsed_final.css("script") if "eval" in e.text()]
            deoffus = deoffuscator(offuscated_function[0])
            try:            
                player_object = demjson.decode(deoffus.split("playerInstance.setup(")[1].split("tracks:")[0] + "}")
                
                return Video(referer=action_v4,thumb=player_object.get("image"), type_=player_object.get("sources").get("type"), stream=player_object.get("sources").get("file"))
            except:
                many_ofs = [deoffuscator(i) for i in offuscated_function if "m3u8" in i]
                final_ofs = many_ofs[0].split("player(")[-1].split(");")[0].replace("'", "").replace(" ", "").split(",")
                
                return Video(referer=action_v4,thumb=final_ofs[1], type_="hls", stream=final_ofs[0])
        
        else:
            return None
        
        
    def search_episodes(self, title:str) -> Episodes:
        """Pass anime series name and return a list of episodes by season"""
        # TODO: Solve season connection between loacal database(based in anilist) and animeshouse model
        # TODO: Type of slang is wrong in some animes title from new episode, they don't match with the name on anime page and search(animeshouse) not return correct value
        #FIX: now it's works well with animes who have more then one season, need more abstraction
        title_changed = "-".join(title.split('-e')[0].split('-',-1)[:-1])
        
        req = self._make_request("GET", url=ANIME_PAGE.format(title_changed), headers=self.headers)
        parse = self.parse(req.text)
        episodes_by_seasons = [(int(e.css_first("span.se-t").text()), [a.attrs["href"] for a in e.css("a")]) for e in [i for i in parse.css_first("div#seasons").css("div.se-c")]]
        
        local_data = self.database.get_all_by_title(title_changed.replace("-", " "))
        data = [(i["_id"], i["card"]["title"]) for i in sorted(local_data, key=lambda x: x["card"].get("year"),reverse=True)]
        resp = []
        
        for idx, seasons in enumerate(episodes_by_seasons[::-1]):
            resp.append(
                Episodes(
                    _id=data[idx][0],
                    title=data[idx][1],
                    season=seasons[0],
                    episodes=seasons[1]
                )
            )
        return resp
       
        