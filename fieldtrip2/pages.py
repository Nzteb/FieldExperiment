from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Contribution(Page):
    form_model = 'player'
    form_fields = ['binary_choice']


class Voting(Page):
    def is_displayed(self):
        return self.session.config['treatment'] == 'sanction'
    form_model = 'player'
    form_fields = ['vote']


class VotingWaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(self):
        return self.session.config['treatment'] == 'sanction'

    # when waiting for all groups this is only called once in total
    def after_all_players_arrive(self):
        for group in self.subsession.get_groups():
            group.define_bonus()


class DecisionResults(Page):
    # initilize template variables to display on the page
    def vars_for_template(self):
        # keys of var_dic are the variable names in the template
        var_dic = {}
        map_choices = {1:'Kept points',2: 'Gave to account'}
        map_votes = {1: 'Keeper', 2:'Giver', 3:'No one'}
        map_bonus = {1: 'Yes', 0:'No'}
        for player in self.group.get_players():
            labelstripped = player.label.replace(' ', '')
            var_dic[labelstripped + '_choice' ] = map_choices[player.binary_choice]
            var_dic[labelstripped + '_vote'] = map_votes[player.vote]
            var_dic[labelstripped + '_bonus'] = map_bonus[player.gets_bonus]

        return var_dic









page_sequence = [
    Contribution,
    Voting,
    VotingWaitPage,
    DecisionResults,

]
