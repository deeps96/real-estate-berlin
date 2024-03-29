from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.vermietung-optima.berlin/immobilien.xhtml?f%5B2084-134%5D=ind_Schl_2546&f%5B2084-4%5D=0&f%5B2084-2%5D=0&f%5B2084-6%5D=miete&f%5B2084-8%5D=wohnung&f%5B2084-90%5D=openGeoDb_Region_152675%2CopenGeoDb_Region_152673%2CopenGeoDb_Region_152597&f%5B2084-88%5D=&f%5B2084-16%5D=&f%5B2084-82%5D=&f%5B2084-84%5D=&f%5B2084-153%5D='


class Optima(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Optima'
            }
            for link in browser.links(link_text='Alle Objektdetails')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=get_address(browser.page),
            email=browser.page.select('a[href^=mailto\:]')[0]['href'][len('mailto:'):],
            images=[
                link['href']
                for link in browser.page.select('.obj-gallery ul a')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Gesamtmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmeranzahl'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche')).group()),
            title=browser.page.title.text
        )
        browser.close()
        return offer


def get_address(page: BeautifulSoup) -> str:
    return f"" \
           f"{extract_information_from_table(page, 'Strasse')} " \
           f"{extract_information_from_table(page, 'Hausnummer')}, " \
           f"{extract_information_from_table(page, 'Ort')} " \
           f"{extract_information_from_table(page, 'PLZ')}"


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next((
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == attribute
    ), 'NaN')
