from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.buwog-immobilientreuhand.de/de/property-search-result?property_search%5Btype%5D=rent&property_search%5Blimit%5D=10&property_search%5Blocation_rent%5D=city_1&property_search%5Blocation_buy%5D=&property_search%5Bproperty_type%5D=living&property_search%5Bmaximum_price%5D=1000&property_search%5Bminimum_number_of_rooms%5D=1&property_search%5Bmaximum_number_of_rooms%5D=0&property_search%5Bminimum_area%5D=40&property_search%5Bmaximum_area%5D=0&property_search%5Bbeing_built%5D=1&property_search%5Bexisting%5D=1&property_search%5Bcountry%5D=de&property_search%5Bsorting%5D=updatedAt%7CDESC'


class Buwog(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Buwog'
            }
            for link in browser.page.select('.b-immo-result a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=browser.page.select('.object-number strong')[0].text,
            email=None,
            images=[
                urljoin(OFFER_LIST, img['src'])
                for img in browser.page.select('.slider-wrap img')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Mietpreis (gesamt):').replace('.', '')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Anzahl ganze Zimmer:'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Fläche:')).group()),
            title=browser.page.find('h1').text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next((
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == attribute
    ), 'NaN')
