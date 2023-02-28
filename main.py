from animeshouse.api import AnimesHouse
import json

if __name__ == "__main__":
    ah = AnimesHouse()
    resp = ah.get_news_episodes_by_page(page=1)
    
    with open("teste.json", "w", encoding="utf-8") as f:
        f.write(json.dumps([i.__dict__ for i in resp], indent=4, ensure_ascii=False))
    