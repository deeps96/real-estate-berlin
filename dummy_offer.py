from offer import Offer
from travel_time import TravelTime


dummy_offer = Offer(
    address='Chausseestraße 60b, Berlin 10115',
    email='aoswald@optima-gmbh.de',
    images=[
        'https://image.onoffice.de/smart20/Objekte/TrialogGmbh/20925/Foto_193027.jpg@800x600',
        'https://image.onoffice.de/smart20/Objekte/TrialogGmbh/20925/Titelbild_193021.jpg@800x600',
        'https://image.onoffice.de/smart20/Objekte/TrialogGmbh/20925/Foto_193023.jpg@800x600',
        'https://image.onoffice.de/smart20/Objekte/TrialogGmbh/20925/Foto_193025.jpg@800x600',
        'https://image.onoffice.de/smart20/Objekte/TrialogGmbh/20925/Foto_193029.jpg@800x600'
    ],
    link='https://www.vermietung-optima.berlin/immobilien.xhtml?id[obj0]=20925',
    rent={
        'price': 694.97,
        'total': True
    },
    rooms='1',
    size=35,
    title='Etagenwohnung in Berlin',
    travel_times=[
        TravelTime(target='Edeka', bike='2 min'),
        TravelTime(target='Netlight', bike='2 min', public='2 min'),
        TravelTime(target='S-Bahn', bike='2 min'),
        TravelTime(target='U-Bahn', bike='2 min')
    ]
)
