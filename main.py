from animeshouse.api import AnimesHouse
import json

def main():
    ah = AnimesHouse()
    resp = ah.get_news_episodes_by_page(page=1)
    # req = json.loads(open("teste.json", encoding="utf-8").read())
    # resp = ah.get_videos_external_links(req[0].get("link"))
    # print(req[0].get("title"))
    # resp = ah.search_episodes(req[0].get("link"))
    print(resp)
    return resp
    
if __name__ == "__main__":
    main()