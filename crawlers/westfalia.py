from re import search
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.westfalia-gmbh.de/immobilienfilter/?cmwp_search_nonce=deddf423a4&nutzungsart=28&vermarktungsart=29&bundesland=210&stadt=229&cm_nettokaltmiete-max=9999999999&cm_gesamtflaeche-max=9999999999&init-results=1'


class Westfalia(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda absolute_link=link['href']: self.get_offer(absolute_link),
                'offer': BaseOffer(link=link['href']),
                'crawler': 'Westfalia'
            }
            for link in browser.page.select("a[title='Zur Immobilie']")
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=f"{extract_information_from_table(browser.page, 'Straße:')}, {extract_information_from_table(browser.page, 'PLZ / Ort:')}",
            email=None,
            images=[
                link['href']
                for link in browser.page.select('.gallery-wrap a')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Warmmiete:')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmer:'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche:')).group()),
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
