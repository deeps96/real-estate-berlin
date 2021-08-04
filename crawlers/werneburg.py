from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://werneburg-immobilien.de/immobilien/'


class Werneburg(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Werneburg'
            }
            for link in browser.page.select('.property-title > a')
            if 'mieten' in link['href']
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=extract_information_from_li_span(browser.page, 'Adresse').replace('\n', ' '),
            email=None,
            images=[
                urljoin(OFFER_LIST, img['src'])
                for img in browser.page.select('.galleria-image img')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_li_span(browser.page, 'Warmmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_li_span(browser.page, 'Zimmer'),
            size=int(search('\d+', extract_information_from_li_span(browser.page, 'Wohnfläche ca.')).group()),
            title=browser.page.select('h1.property-title')[0].text
        )
        browser.close()
        return offer


def extract_information_from_li_span(page: BeautifulSoup, attribute: str) -> str:
    rows = page.select('.property-details div.row')
    return next((
        row.select('div:nth-child(2)')[0].text
        for row in rows
        if row.select('div:first-child') and row.select('div:first-child')[0].text == attribute
    ), default='NaN')
