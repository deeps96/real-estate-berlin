from typing import List, Dict, Any

from mechanicalsoup import StatefulBrowser

from offer import Offer


class Crawler:

    def get_offer_link_list(self) -> List[Dict[str, Any]]:
        pass

    def get_offer(self, link: str) -> Offer:
        pass


def create_browser() -> StatefulBrowser:
    return StatefulBrowser(user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
