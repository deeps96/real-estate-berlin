from re import search
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from requests import get

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

BASE_URL = 'https://www.vonovia.de/de-de/immobiliensuche/'


class Vonovia(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        response = get('https://www.wohnraumkarte.de/Api/getImmoList', params={
            'offset': 0,
            'limit': 100,
            'orderBy': 'date_asc',
            'city': 'Berlin, Deutschland',
            'perimeter': 0,
            'rentType': 'miete',
            'immoType': 'wohnung',
            'priceMax': 1_000,
            'sizeMin': 40,
            'sizeMax': 0,
            'minRooms': 1,
            'dachgeschoss': 0,
            'erdgeschoss': 0,
            'sofortfrei': 'egal',
            'lift': 0,
            'balcony': 'egal',
            'disabilityAccess': 'egal',
            'subsidizedHousingPermit': 'egal'
        })
        offers = [{**offer, 'link': f"{BASE_URL}{offer['slug']}-{offer['wrk_id']}"} for offer in response.json()['results']]
        return [
            {
                'fetch': lambda offer=offer: self.get_offer(offer),
                'offer': BaseOffer(link=offer['link']),
                'crawler': 'Vonovia'
            }
            for offer in offers
        ]

    def get_offer(self, offer: Dict[str, Any]) -> Offer:
        browser = create_browser()
        browser.open(offer['link'])
        offer = Offer(
            address=extract_information_from_li(browser.page, 'Adresse'),
            email=None,
            images=[
                offer['preview_img_url']
            ],
            link=offer['link'],
            rent={
                'price': int(search('\d+', extract_information_from_li(browser.page, 'Warmmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_li(browser.page, 'Anzahl Zimmer'),
            size=int(search('\d+', extract_information_from_li(browser.page, 'Wohnfläche')).group()),
            title=browser.page.select('header.expose__headline h1')[0].text
        )
        browser.close()
        return offer


def extract_information_from_li(page: BeautifulSoup, attribute: str) -> str:
    lis = page.find_all('li')
    return next((
        li.select('span.value')[0].text
        for li in lis
        if li.select('span.label') and li.select('span.label')[0].text.strip() == attribute
    ), default='NaN')
