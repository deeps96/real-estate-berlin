from collections import Counter
from time import sleep
from typing import List, Dict, Any

from config import user_id, interval_in_seconds
from crawlers.adler import Adler
from crawlers.akelius import Akelius
from crawlers.degewo import Degewo
from crawlers.deutsche_wohnen import DeutscheWohnen
from crawlers.foelske import Foelske
from crawlers.gewobag import Gewobag
from crawlers.habitare import Habitare
from crawlers.howoge import Howoge
from crawlers.milia import Milia
from crawlers.optima import Optima
from crawlers.stadt_und_land import StadtUndLand
from crawlers.westfalia import Westfalia
from offer import Offer
from offer_storage import OfferStorage
from telegram_bot import TelegramBot

CRAWLERS = [
    Howoge(),
    Gewobag(),
    Degewo(),
    Optima(),
    DeutscheWohnen(),
    StadtUndLand(),
    Adler(),
    Westfalia(),
    Milia(),
    Foelske(),
    Habitare(),
    Akelius()
]


def fetch_offers() -> List[Dict[str, Any]]:
    print('Fetching...')
    offers = []
    for crawler in CRAWLERS:
        try:
            offers.extend(crawler.get_offer_link_list())
        except Exception as e:
            print(e)
    return offers


def is_interesting_offer(offer: Offer) -> bool:
    return (offer.zip.startswith('10') or offer.zip in ['12047', '12049', '12043', '12053']) and offer.rent['price'] < 1_000


if __name__ == '__main__':
    offer_storage = OfferStorage()
    bot = TelegramBot(offer_storage)
    offers = fetch_offers()
    offer_storage.add_offers([
        offer['offer']
        for offer in offers
    ])
    print(f'Found {str(offer_storage.get_size())} offers.')
    stats = Counter(offer['crawler'] for offer in offers)
    bot.send_stats(user_id, stats)
    try:
        while True:
            sleep(interval_in_seconds)
            new_offers = []
            for offer in fetch_offers():
                if offer_storage.has_offer(offer['offer'].id):
                    continue
                try:
                    new_offers.append(offer['fetch']())
                except Exception as e:
                    bot.send_error_message(user_id, str(e))
                    offer_storage.add_offer(offer['offer'])
            if new_offers:
                print(f'Found {len(new_offers)} new offers')
                offer_storage.add_offers(new_offers)
                for new_offer in new_offers:
                    if is_interesting_offer(new_offer):
                        try:
                            bot.send_offer(user_id, new_offer)
                        except:
                            print(new_offer)
    finally:
        bot.stop()
        bot.send_shutdown_notice(user_id)
