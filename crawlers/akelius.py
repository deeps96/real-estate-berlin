from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://rent.akelius.com/de/search/germany/apartment/berlin?borough=charlottenburg-wilmersdorf,friedrichshain,kreuzberg,mitte,prenzlauer%20berg,sch%C3%B6neberg,wei%C3%9Fensee&order=asc&sortby=lastPublishedDate'


class Akelius(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Akelius'
            }
            for link in browser.page.select('.item a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=f"{browser.page.find('div', class_='headline-container').text}, {browser.page.find('div', class_='detail-main-address').text}",
            email=None,
            images=[
                image['src']
                for image in browser.page.select('.detail-gallery img')
            ],
            link=link,
            rent={
                'price': int(search('\d+', browser.page.select('.amount')[0].text).group()),
                'total': True
            },
            rooms=browser.page.select('.detail-main-facts p:first-child')[0].text,
            size=int(search('\d+', browser.page.select('.detail-main-facts p:nth-child(2)')[0].text).group()),
            title=browser.page.find('div', class_='headline-container').text
        )
        browser.close()
        return offer
