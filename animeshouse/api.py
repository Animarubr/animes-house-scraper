from selectolax.parser import HTMLParser
from urllib.parse import unquote
from typing import List, Dict
from datetime import datetime
import demjson
import re

from .session import Session
from .utils import *
from .types import *
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
                s = links[index].split("-episodio")[0].split("-")[-1]
                _id = self.database.get_anime_by_title(titles[index])
                # print(titles[index], _id, s)
                # print()
                card = Card(
                    anime_id=_id,
                    title=titles[index],
                    season=s,
                    image=i,
                    link=links[index],
                    episode=episodes[index],
                    episode_slang=slangs[index],
                    is_censored=is_censored[index],
                    created_at=str(datetime.utcnow())
                )
                add_to_cache = self.database.add_to_cache(card.__dict__)
                print(add_to_cache)
                if "Success!" in add_to_cache:
                    print("[STATUS] ", add_to_cache)
                    response.append(card)
                else:
                    print("[STATUS] ", add_to_cache)
            
            return response
        return None
    
    def get_videos_external_links(self, slang_episode:str, type_of:str="anime") -> List[Video]|None:

        if type_of == 'anime':
            url_encode = EPISODE_VIDEO_PAGE
        else:
            url_encode = MOVIE_VIDEO_PAGE
        
        request_news_episodes = self._make_request(method="GET", url=url_encode.format(slang_episode), headers=self.headers)
        
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
            headers["referer"] = url_encode.format(slang_episode)
            
            request_ajax = self._make_request(method="POST", url=VIDEO_IFRAME_BUILDER, data=payload, headers=headers)
            iframe_parse = self.parse(request_ajax.text)
            base_iframe_uri = iframe_parse.css_first("iframe").attrs["src"]
            
            request_iframe = self._make_request(method="GET", url=f"{BASE_ROOT}{base_iframe_uri}", headers=self.headers)
            external_link_parse = self.parse(request_iframe.text)

            response.append(external_link_parse.css_first("a").attrs["href"])

        # streams = [self._get_streams(e, url_encode.format(slang_episode), type_of) for e in response]
        streams = []
        for stream in response:
            try:
                st = self._get_streams(stream, url_encode.format(slang_episode), type_of)
                streams.append(st)
            except Exception as e:
                print(str(e))
                
        return streams
    
    def _get_streams(self, external_link:str, slang_episode:str, type_of:str="anime") -> Video|None:
        #TODO: Needs to refatoration
        
        self.headers["referer"] = EPISODE_VIDEO_PAGE.format(slang_episode) if type_of == "anime" else MOVIE_VIDEO_PAGE.format(slang_episode)
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
            try:
                deoffus = deoffuscator(offuscated_function[0])
                player_object = demjson.decode(deoffus.split("playerInstance.setup(")[1].split("tracks:")[0] + "}")
                
                return Video(referer=action_v4,thumb=player_object.get("image"), type_=player_object.get("sources").get("type"), stream=player_object.get("sources").get("file"))
            except Exception:
                many_ofs = [deoffuscator(i) for i in offuscated_function if "m3u8" in i]
                final_ofs = many_ofs[0].split("player(")[-1].split(");")[0].replace("'", "").replace(" ", "").split(",")
                
                return Video(referer=action_v4,thumb=final_ofs[1], type_="hls", stream=final_ofs[0])
        
        else:
            return None
        
        
    def search_episodes(self, title:str) -> Episodes:
        """Pass anime series name and return a list of episodes by season"""
        title_changed = title.replace(" ", "-").lower()
        print(title_changed)
        
        if " - " in  title[-7:]:
            if "dublado" not in title.lower():
                title_changed = title[:-7].replace(" ", "-").lower()
            else:
                title_changed = title[:-7].replace(" - Dublado", " Dublado").replace(" ", "-").lower()
        
        title_changed = re.sub('[^a-zA-Z0-9\- \n\.]', '', title_changed)
        
        local_data = self.database.get_all_by_title(title_changed.replace("-", " "))
   
        data = [(i["_id"], i["card"]["title"]) for i in sorted(local_data, key=lambda x: x["inside_data"].get("year") if x["inside_data"].get("year") is not None else 0,reverse=True)] if local_data is not None else []

        req = self._make_request("GET", url=ANIME_PAGE.format(title_changed), headers=self.headers)
        parse = self.parse(req.text)
        if "ERROR 404" in str(parse.text()):
            title_3 = " ".join(title.split(" ")[:2])
            req = self._make_request("GET", url=SEARCH_ENDPOINT.format(title_3), headers=self.headers)
            parse = self.parse(req.text)
            searchied = [[(e.text(), e.css_first("a").attrs["href"], i.css_first("span").text().lower()) for e in i.css("div.title")] for i in parse.css("div.result-item")]
            if len(searchied) < 0:
                return []
            
            s_rank = []

            for i in searchied:                    
                s_rank.append([check_is_same(title, i[0][0]), i[0]])
                        
            smax = sorted(s_rank, key=lambda x: x[0], reverse=True)[0][1]
            if smax[-1] != "filme":
                req = self._make_request("GET", url=ANIME_PAGE.format(smax[1].split("/")[4]), headers=self.headers)
                parse = self.parse(req.text)

                if "ERROR 404" in str(parse.text()):
                    return []
            else:
                _id = None
                if len(data) > 0:
                    _id = data[0][0]
                    title = data[0][1]
                    
                link = smax[1].split("/")[4]
                return Movie(_id=_id, title=title, type_of='movie', movie_number=1, link=link)

        episodes_by_seasons = [(int(e.css_first("span.se-t").text()), [a.attrs["href"] for a in e.css("a")]) for e in [i for i in parse.css_first("div#seasons").css("div.se-c")]]
        resp = []
        # POSSO SIMPLESMENTE IGNORAR A TEMPORADA CORRETA E RETOR NAR TODOS OS EPIS, SÒ RESOLVER NO FRONT
        for idx, seasons in enumerate(episodes_by_seasons[::-1]):
            _id = None
            if len(data) > 0:
                _id = data[idx][0] if len(data)>=len(episodes_by_seasons) else data[0][0]
                title = data[idx][1] if len(data)>=len(episodes_by_seasons) else data[0][1]
                
            resp.append(
                Episodes(
                    _id=_id,
                    type_of='anime',
                    title=title,
                    season=seasons[0],
                    episodes=seasons[1]
                )
            )
        return resp
       
        