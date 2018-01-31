from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):

        yield(pages.MyPage)
        if self.round_number == 2:
            yield(pages.MyPage2)
        yield(pages.Results)



