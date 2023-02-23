from animeshouse.api import AnimesHouse

if __name__ == "__main__":
    ah = AnimesHouse()
    print(ah.get_news_episodes_by_page(page=2))
    