from time import sleep
from typing import List, Dict, Any

from config import user_id, interval_in_seconds
from crawlers.adler import Adler
from crawlers.degewo import Degewo
from crawlers.deutsche_wohnen import DeutscheWohnen
from crawlers.gewobag import Gewobag
from crawlers.howoge import Howoge
from crawlers.optima import Optima
from crawlers.stadt_und_land import StadtUndLand
from crawlers.westfalia import Westfalia
from offer import Offer
from offer_storage import OfferStorage
from telegram_bot import TelegramBot

CRAWLERS = [Howoge(), Gewobag(), Degewo(), Optima(), DeutscheWohnen(), StadtUndLand(), Adler(), Westfalia()]


def fetch_offers() -> List[Dict[str, Any]]:
    return [
        offer
        for crawler in CRAWLERS
        for offer in crawler.get_offer_link_list()
    ]


def is_interesting_offer(offer: Offer) -> bool:
    return (offer.zip.startswith('10') or offer.zip in ['12047', '12049', '12043', '12053']) and offer.rent['price'] < 1_000


if __name__ == '__main__':
    offer_storage = OfferStorage([
        offer['offer']
        for offer in fetch_offers()
    ])
    print(f'Found {str(offer_storage.get_size())} offers.')
    bot = TelegramBot(offer_storage)
    try:
        while True:
            sleep(interval_in_seconds)
            new_offers = [
                offer['fetch']()
                for offer in fetch_offers()
                if not offer_storage.has_offer(offer['offer'].id)
            ]
            if new_offers:
                print(f'Found {len(new_offers)} new offers')
            offer_storage.add_offers(new_offers)
            for new_offer in new_offers:
                if is_interesting_offer(new_offer):
                    bot.send_offer(user_id, new_offer)
    except KeyboardInterrupt:
        bot.stop()
