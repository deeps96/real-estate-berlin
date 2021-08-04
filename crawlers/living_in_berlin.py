from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.livinginberlin.de/angebote/mieten'


class LivingInBerlin(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Living in Berlin'
            }
            for link in browser.page.select('.uk-card-media-top a')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=f"{extract_information_from_table(browser.page, 'Adresse')} Berlin",
            email=None,
            images=[
                urljoin(OFFER_LIST, img['data-src'])
                for img in browser.page.select('li[data-uk-slideshow-item] img')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_table(browser.page, 'Gesamtmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_table(browser.page, 'Zimmer'),
            size=int(search('\d+', extract_information_from_table(browser.page, 'Wohnfläche')).group()),
            title=browser.page.select('h1')[0].text
        )
        browser.close()
        return offer


def extract_information_from_table(page: BeautifulSoup, attribute: str) -> str:
    dts = page.find_all('dt')
    dds = page.find_all('dd')
    return next((
        dds[i_dt].text
        for i_dt, dt in enumerate(dts)
        if dt.text == attribute
    ), 'NaN')
