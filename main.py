from animeshouse.api import AnimesHouse
import json

def main():
    ah = AnimesHouse()
    # resp = await ah.get_news_episodes_by_page(page=1)
    resp = json.loads(open("teste.json", encoding="utf-8").read())
    uris = ah.get_videos_external_links(resp[0].get("link"))
    return uris
    
if __name__ == "__main__":
    main()