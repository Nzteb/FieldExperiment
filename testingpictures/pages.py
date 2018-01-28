from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'
    form_fields = ['belief_q1']


class MyPage2(Page):
    form_model = 'player'
    form_fields = ['belief_q1']

class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    MyPage,
    MyPage2,
    ResultsWaitPage,
    Results
]