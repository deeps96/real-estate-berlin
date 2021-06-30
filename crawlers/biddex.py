from re import search
from typing import List, Dict, Any
from unicodedata import normalize
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.biddex.de/immobilien/mieten/wohnungen?lat=&lng=&sort%5B0%5D=n%7Cd&city=Berlin&district=&radius=0&zimmer_min=&zimmer_max=&wohnflaeche_min=&wohnflaeche_max=&preis_min=&preis_max=1000'


class Biddex(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Biddex'
            }
            for link in browser.page.select('a.expose-btn')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=extract_address(browser.page),
            email=None,
            images=[
                urljoin(OFFER_LIST, link['href'])
                for link in browser.page.select('a.gallery__thumb')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Miete inkl. NK')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmer'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche')).group()),
            title=browser.page.title.text
        )
        browser.close()
        return offer


def extract_address(page: BeautifulSoup) -> str:
    right_boxes = page.find_all('div', class_='right-box')
    return next(
        normalize('NFKD', right_box.find('p').text)
        for right_box in right_boxes
        if right_box.find('h4', text='Addresse')
    )


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next(
        normalize('NFKD', table_row.select('td:first-child span.pull-right')[0].text)
        for table_row in table_rows
        if table_row.select('td:first-child') and attribute in table_row.select('td:first-child')[0].find_all(text=True, recursive=False)[0]
    )
