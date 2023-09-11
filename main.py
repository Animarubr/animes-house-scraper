from animeshouse.api import AnimesHouse
import json

def main(page=None):
    ah = AnimesHouse()
    resp = ah.get_news_episodes_by_page(page)
    # req = json.loads(open("teste.json", encoding="utf-8").read())
    # resp = ah.get_videos_external_links("isekai-one-turn-kill-neesan-ane-douhan-no-isekai-seikatsu-hajimemashita-s1-episodio-4-legendado-hd")
    # resp = ah.get_videos_external_links("jujutsu-kaisen-0", type_of="filme")
    # print(req[0].get("title"))
    # resp = ah.search_episodes("Jujutsu Kaisen 0 Movie")
    print(resp)
    return resp
    
if __name__ == "__main__":
    page = input("digite a pagina: ")
    # main()
    main(page)