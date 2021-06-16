import re
from dataclasses import dataclass
from hashlib import md5
from typing import List, Any, Dict, Optional

from prettytable import PrettyTable

from base_offer import BaseOffer
from config import width_in_characters
from travel_time import TravelTime


@dataclass()
class Offer(BaseOffer):
    address: str
    email: Optional[str]
    images: List[str]
    link: str
    rent: Dict[str, Any]
    rooms: str
    size: int
    title: str
    travel_times: Optional[List[TravelTime]] = None
    id: str = None
    zip: str = None

    def __post_init__(self):
        self.id = md5(self.link.encode()).hexdigest()
        zip_regex_match = re.search('\d{5}', self.address)
        self.zip = zip_regex_match and zip_regex_match.group()

    def get_meta_table(self) -> PrettyTable:
        meta_table = PrettyTable(
            field_names=['key', 'value'],
            header=False,
            min_table_width=width_in_characters,
            border=False,
            padding_width=0
        )
        meta_table.align['key'] = 'l'
        meta_table.align['value'] = 'r'
        meta_table.add_rows([
            ['Rooms', str(self.rooms)],
            ['Size', f"{self.size} m²"],
            [f"Price ({'warm' if self.rent['total'] else 'kalt'})", f"{self.rent['price']} €"]
        ])
        return meta_table

    def get_travel_table(self) -> PrettyTable:
        travel_table = PrettyTable(
            field_names=['Destination', 'Bike'],
            min_table_width=width_in_characters,
            border=False,
            padding_width=0
        )
        travel_table.align['Destination'] = 'l'
        travel_table.align['Bike'] = 'r'
        travel_table.add_rows(
            [travel_time.target, travel_time.bike]
            for travel_time in self.travel_times
        )
        return travel_table

    def generate_offer_message(self) -> str:
        return f'''
<b>{self.title[:width_in_characters]}</b>
<pre>{self.get_meta_table().get_string()}</pre>'''

    def generate_email_body(self) -> str:
        return f'''Sehr geehrte Damen und Herren,

ich interessiere mich für die von Ihnen angebotene Mietwohnung in der {self.address}.
Ich schließe momentan mein Studium ab und werde im August eine Stelle als IT-Consultant beginnen.
Der Arbeitsvertrag ist unbefristet, bereits unterschrieben und sieht eine Vergütung von 3000 Euro Netto vor.
Ich würde als einzige Person in die Wohnung einziehen. Ich bin Nichtraucher und halte keine Haustiere.
Alle erforderlichen Unterlagen liegen vor oder können kurzfristig zusammengestellt werden.
Für die anfängliche Probezeit von sechs Monaten, haben sich meine Eltern (beide Beamte) bereit erklärt ggf. eine Bürgschaft zu leisten.
Wäre es möglich, die Wohnung vor Ort zu besichtigen?

Mit freundlichen Grüßen,
Leonardo Hübscher'''
