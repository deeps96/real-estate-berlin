from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://immosuche.degewo.de/de/search?size=10&page=1&property_type_id=1&categories%5B%5D=1&lat=&lon=&area=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district=46%2C+28%2C+71%2C+60&property_number=&price_switch=true&price_radio=custom&price_from=&price_to=&qm_radio=null&qm_from=&qm_to=&rooms_radio=null&rooms_from=&rooms_to=&wbs_required=&order=rent_total_without_vat_asc'


class Degewo(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        return [
            {
                'fetch': lambda: self.get_offer(urljoin(OFFER_LIST, link['href'])),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Degewo'
            }
            for link in browser.page.select('article > a')
        ]

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        return Offer(
            address=browser.page.find('p', class_='gallery__lead').text.replace('\n', ' '),
            email=None,
            images=[
                urljoin(OFFER_LIST, link['href'])
                for link in browser.page.select('a.gallery__thumb')
            ],
            link=link,
            rent={
                'price': int(browser.page.find('div', class_='expose__price-tag').next.replace('\n', '').split(',', 1)[0]),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmer'),
            size=int(extract_information_from_table(browser.page, 'Wohnfläche').split(',', 1)[0]),
            title=browser.page.title.text
        )


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next(
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == attribute
    )
