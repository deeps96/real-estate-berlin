from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.wbm.de/wohnungen-berlin/angebote/'


class WBM(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'WBM'
            }
            for link in browser.page.select('article a[title=Details]')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=browser.page.select('p.address')[0].text,
            email=None,
            images=[
                urljoin(OFFER_LIST, img['src'])
                for img in browser.page.select('div[id=images] img')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_li_span(browser.page, 'Warmmiete:')).group()),
                'total': True
            },
            rooms=extract_information_from_li(browser.page, 'Anzahl der Zimmer:'),
            size=int(search('\d+', extract_information_from_li(browser.page, 'Größe:')).group()),
            title=browser.page.select('h2.imageTitle')[0].text
        )
        browser.close()
        return offer


def extract_information_from_li_span(page: BeautifulSoup, attribute: str) -> str:
    lis = page.find_all('li')
    return next((
        li.select('span:nth-child(2)')[0].text
        for li in lis
        if li.select('span:first-child') and li.select('span:first-child')[0].text == attribute
    ), 'NaN')


def extract_information_from_li(page: BeautifulSoup, attribute: str) -> str:
    lis = page.find_all('li', class_='main-property')
    return next((
        li.contents[2].replace(' ', '')
        for li in lis
        if li.select('span') and li.select('span')[0].text == attribute
    ), 'NaN')
