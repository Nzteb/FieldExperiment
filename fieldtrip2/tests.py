from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):


        yield (pages.Belief, {'belief_q1':1, 'belief_q2':1, 'belief_q3':1})
