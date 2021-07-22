from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.berlinovo.de/de/suche-wohnungen?f[0]=field_territorial_entity%3A194&f[1]=field_real_estate_category%3A197&f[2]=field_territorial_entity%3A194&f[3]=field_net_area%3A%5B40%20TO%2080%5D'


class Berlinovo(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Berlin'
            }
            for link in browser.page.select('#main .views-field-field-image a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=browser.page.find('span', class_='address').text.replace('\n', ' '),
            email=None,
            images=[
                urljoin(OFFER_LIST, link['href'])
                for link in browser.page.select('ul.ad-thumb-list a')
            ],
            link=link,
            rent={
                'price': int(search('\d+', browser.page.select('div.views-field-field-total-rent span.field-content')[0].text).group()),
                'total': True
            },
            rooms=browser.page.select('div.views-field-field-rooms span.field-content')[0].text,
            size=int(search('\d+', browser.page.select('div.views-field-field-net-area-1 span.field-content')[0].text).group()),
            title=browser.page.select('h1')[0].text
        )
        browser.close()
        return offer
