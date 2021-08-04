from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://portal.immobilienscout24.de/ergebnisliste/29381946/1?sid=23059h68ouaa8o7hfc8dhbbov2'


class RWLiving(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'R&W Living'
            }
            for link in browser.page.select('.result__list--element h3 > a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=browser.page.find('div', class_='expose--text__address').text.replace('\n', ''),
            email=None,
            images=[
                urljoin(OFFER_LIST, img['src'][:img['src'].index('/ORIG')])
                for img in browser.page.select('img.sp-thumbnail')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Gesamtmiete:')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmer:'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche ca.:')).group()),
            title=browser.page.select('.is24__block__responsive--col1 .expose--text > h4')[0].text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('li')
    return next((
        table_row.select('p:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('p:first-child') and table_row.select('p:first-child')[0].text == attribute
    ), default='NaN')

