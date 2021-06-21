from re import search
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base_offer import BaseOffer
from crawlers.crawler import Crawler, create_browser
from offer import Offer

OFFER_LIST = 'https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/?bezirke%5B%5D=charlottenburg-wilmersdorf-charlottenburg&bezirke%5B%5D=friedrichshain-kreuzberg&bezirke%5B%5D=friedrichshain-kreuzberg-friedrichshain&bezirke%5B%5D=friedrichshain-kreuzberg-kreuzberg&bezirke%5B%5D=mitte&bezirke%5B%5D=mitte-gesundbrunnen&bezirke%5B%5D=mitte-tiergarten&bezirke%5B%5D=pankow-prenzlauer-berg&bezirke%5B%5D=tempelhof-schoeneberg&bezirke%5B%5D=tempelhof-schoeneberg-lichtenrade&bezirke%5B%5D=tempelhof-schoeneberg-mariendorf&bezirke%5B%5D=tempelhof-schoeneberg-schoeneberg&nutzungsarten%5B%5D=wohnung&gesamtmiete_von=&gesamtmiete_bis=1000&gesamtflaeche_von=&gesamtflaeche_bis=&zimmer_von=&zimmer_bis='


class Gewobag(Crawler):

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        browser = create_browser()
        browser.open(OFFER_LIST)
        offers = [
            {
                'fetch': lambda rel_link=link['href']: self.get_offer(urljoin(OFFER_LIST, rel_link)),
                'offer': BaseOffer(link=urljoin(OFFER_LIST, link['href'])),
                'crawler': 'Gewobag'
            }
            for link in browser.page.find('div', class_='filtered-elements').find_all('a', text='Mietangebot ansehen')
        ]
        browser.close()
        return offers

    def get_offer(self, link: str) -> Offer:
        browser = create_browser()
        browser.open(link)
        offer = Offer(
            address=extract_information_from_li_div(browser.page, 'Anschrift'),
            email=None,
            images=[
                img['src']
                for img in browser.page.select('.slider img[alt!=Phishing-Hinweis]')
            ],
            link=link,
            rent={
                'price': int(search('\d+', extract_information_from_li_div(browser.page, 'Gesamtmiete')).group()),
                'total': True
            },
            rooms=extract_information_from_li_div(browser.page, 'Anzahl Zimmer'),
            size=int(search('\d+', extract_information_from_li_div(browser.page, 'Fläche in m²')).group()),
            title=browser.page.title.text
        )
        browser.close()
        return offer



def extract_information_from_li_div(page: BeautifulSoup, attribute: str) -> str:
    lis = page.find_all('li')
    return next(
        li.select('div:nth-child(2)')[0].text
        for li in lis
        if li.select('div:first-child') and li.select('div:first-child')[0].text == attribute
    )
