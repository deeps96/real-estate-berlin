from typing import List, Dict, Optional

from base_offer import BaseOffer


class OfferStorage:

    def __init__(self, offers: List[BaseOffer]):
        self.offers = dictify_offers(offers)

    def has_offer(self, offer_id: str) -> bool:
        return offer_id in self.offers

    def get_offer(self, offer_id: str) -> Optional[BaseOffer]:
        return self.offers.get(offer_id)

    def add_offers(self, offers: List[BaseOffer]) -> None:
        self.offers.update(dictify_offers(offers))

    def get_size(self) -> int:
        return len(self.offers)


def dictify_offers(offers: List[BaseOffer]) -> Dict[str, BaseOffer]:
    return {
        offer.id: offer
        for offer in offers
    }

