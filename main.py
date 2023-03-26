from animeshouse.api import AnimesHouse
import json

def main():
    ah = AnimesHouse()
    # resp = await ah.get_news_episodes_by_page(page=1)
    resp = json.loads(open("teste.json", encoding="utf-8").read())
    print(ah.get_videos_external_links(resp[0].get("link")))
    return resp
    
if __name__ == "__main__":
    main()
    # resp = asyncio.run(main())
    # with open("teste.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps([i.__dict__ for i in resp], indent=4, ensure_ascii=False))
    