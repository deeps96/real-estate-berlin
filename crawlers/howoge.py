from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import post

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

BASE_URL = 'https://www.howoge.de/'


class Howoge(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        response = post('https://www.howoge.de/?type=999&tx_howsite_json_list[action]=immoList', data={
            'tx_howsite_json_list[page]': 1,
            'tx_howsite_json_list[limit]': 100,
            'tx_howsite_json_list[lang]': 0,
            'tx_howsite_json_list[rent]': 1000,
            'tx_howsite_json_list[area]': '',
            'tx_howsite_json_list[rooms]': 'egal',
            'tx_howsite_json_list[wbs]': 'all-offers'
        })
        return [
            {
                'fetch': lambda: self.get_offer(offer),
                'offer': BaseOffer(link=urljoin(BASE_URL, offer['link'])),
                'crawler': 'Howoge'
            }
            for offer in response.json()['immoobjects']
        ]

    def get_offer(self, offer: Dict[str, Any]) -> Offer:
        browser = create_browser()
        browser.open(urljoin(BASE_URL, offer['link']))
        return Offer(
            address=offer['title'],
            email=None,
            images=[
                urljoin(BASE_URL, img['src'])
                for img in browser.page.select('.lightbox-gallery img')
            ],
            link=urljoin(BASE_URL, offer['link']),
            rent={
                'price': int(offer['rent']),
                'total': True
            },
            rooms=str(offer['rooms']),
            size=int(offer['area']),
            title=offer['notice']
        )


if __name__ == '__main__':
    howoge = Howoge()
    print(howoge.get_offer_link_list()[0]['fetch']())
