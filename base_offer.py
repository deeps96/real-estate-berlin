from hashlib import md5


class BaseOffer:

    def __init__(self, link: str):
        self.link = link
        self.id = md5(self.link.encode()).hexdigest()
