from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.core-berlin.de/de/vermietung'


class CoreBerlin(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        browser.select_form('form[action="/de/vermietung?task=properties.search"]')
        browser['filter_type_id'] = 'Wohnung'
        browser['filter_town_id'] = 'Berlin'
        browser.submit_selected()
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Core-Berlin'
            }
            for link in browser.page.select('a[title=Detail]')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=browser.page.find('address').text.replace('\n', ' '),
            email=None,
            images=[
                urljoin(OFFER_LIST, img['src'])
                for img in browser.page.select('#jea-gallery img')
            ],
            link=link,
            rooms=extract_information_from_table(browser.page, 'Zimmer'),
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Gesamtmiete')).group()),
                'total': True
            },
            size=int(search('\d+', extract_information_from_table(browser.page, 'Größe')).group()),
            title=browser.page.select('h2')[0].text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next(
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == attribute
    )


if __name__ == '__main__':
    print(CoreBerlin().get_offer_link_list()[0]['fetch']())
