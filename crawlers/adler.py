from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.adler-group.com/immobiliensuche/wohnung?geocodes=1276003001&livingspace=0&numberofrooms=1&page=10&price=1000&sortby=firstactivation'


class Adler(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Adler'
            }
            for link in browser.page.select('.object-headline > a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=','.join(
                sub_address.text
                for sub_address in browser.page.find_all('span', class_='location-address-text')
            ),
            email=None,
            images=[
                image['src']
                for image in browser.page.select('img.image-covered')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Warmmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Anzahl Zimmer')[1:-len(' Zimmer ')],
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche')).group()),
            title=browser.page.title.text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next(
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == f" {attribute} "
    )

