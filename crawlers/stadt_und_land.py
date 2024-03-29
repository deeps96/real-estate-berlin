from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.stadtundland.de/Wohnungssuche/Wohnungssuche.php?form=stadtundland-expose-search-1.form&sp%3AroomsFrom%5B%5D=1&sp%3AroomsTo%5B%5D=&sp%3ArentPriceFrom%5B%5D=&sp%3ArentPriceTo%5B%5D=1000&sp%3AareaFrom%5B%5D=40&sp%3AareaTo%5B%5D=&sp%3Afeature%5B%5D=__last__&action=submit'


class StadtUndLand(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Stadt und Land'
            }
            for link in browser.links(link_text='weitere Informationen')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=extract_information_from_table(browser.page, 'Adresse'),
            email=None,
            images=[
                urljoin(OFFER_LIST, image['src'])
                for image in browser.page.select('img.SP-Image')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Warmmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Anzahl der Zimmer'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche / Nutzfläche')).group()),
            title=browser.page.title.text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next((
        table_row.select('td')[0].text
        for table_row in table_rows
        if table_row.select('th') and table_row.select('th')[0].text == attribute
    ), 'NaN')

