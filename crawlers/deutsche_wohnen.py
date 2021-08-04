from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import post

from base_offer import BaseOffer
from crawlers.crawler import Crawler
from offer import Offer


class DeutscheWohnen(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        response = post('https://immo-api.deutsche-wohnen.com/estate/findByFilter', json={
            'infrastructure': {},
            'flatTypes': {},
            'other': {},
            'commercializationType': 'rent',
            'utilizationType': 'flat',
            'price': '1000',
            'location': 'Berlin',
            'city': 'Berlin',
            'area': '40'
        })
        return [
            {
                'fetch': lambda offer=offer: self.get_offer(offer),
                'offer': BaseOffer(link=f"https://www.deutsche-wohnen.com/expose/object/{offer['id']}"),
                'crawler': 'Deutsche Wohnen'
            }
            for offer in response.json()
        ]

    def get_offer(self, offer: Dict[str, Any]) -> Offer:
        return Offer(
            address=f"{offer['address']['street']} {offer['address']['houseNumber']}, {offer['address']['zip']} {offer['address']['city']}",
            email=None,
            images=[
                urljoin('https://immo-api.deutsche-wohnen.com/', image['filePath'])
                for image in offer['images']
            ],
            link=f"https://www.deutsche-wohnen.com/expose/object/{offer['id']}",
            rent={
                'price': int(offer['price']),
                'total': offer['heatingCostsIncluded']
            },
            rooms=str(offer['rooms']),
            size=int(offer['area']),
            title=offer['title']
        )


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    table_rows = page.find_all('tr')
    return next((
        table_row.select('td:nth-child(2)')[0].text
        for table_row in table_rows
        if table_row.select('td:first-child') and table_row.select('td:first-child')[0].text == attribute
    ), default='NaN')
