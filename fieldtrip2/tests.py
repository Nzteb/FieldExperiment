from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):

        # one shot and repititions
        if self.round_number == 1:
            yield (pages.Belief, {'belief_q1':1, 'belief_q2':1, 'belief_q3':1})
        else:
            yield (pages.Belief, {'belief_q3': 1})

        if self.round_number == 1:
            yield(pages.DynamicBreakPoint1, {'breakpoint1': 1234})
        yield (pages.Contribution, {'binary_choice':1})
        yield (pages.Voting, {'vote':1})
        yield(pages.Results)

        # test, if they all not get bonus
        assert self.player.gets_bonus == False

        if self.round_number == 1:
            yield(pages.DynamicBreakPoint1, {'breakpoint1': 2468})


        # elicitation
        if self.round_number == Constants.num_rounds:
            yield (pages.DynamicBreakPoint2, {'breakpoint2': 9988})
            #TODO condition treatments here
            yield (pages.Elicitation1, {'risk_elic': 4})
            yield (pages.DynamicBreakPoint2, {'breakpoint2': 1010})
            yield(pages.Elicitation2, {'amb_elic':3})
            yield(pages.DynamicBreakPoint2, {'breakpoint2': 2018})
            # admin break point
            yield (pages.DynamicBreakPoint2, {'breakpoint2' : 4538})

            if self.player.id_in_group == 1:
                yield(pages.AdminPage, {'elic_question_payed':'risk' , 'round_payed':1 , 'a_good':1})
                yield(pages.GrossPayoff)

                # I calculated his payoff by hand
                assert self.player.gross_payoff == 23







        # if self.round_number == 2:
        #     yield (pages.Belief,{'belief_q1':1, 'belief_q2':1, 'belief_q3':1})
        #     yield (pages.Contribution, {'binary_choice':1})
