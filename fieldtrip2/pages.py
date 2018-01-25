from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


# note: you also have to condition in the template e.g. you cannot have belief_q2 in round 2 there
class Belief(Page):
    form_model = 'player'
    def get_form_fields(self):
        if self.player.round_number == 1:
            return ['belief_q1', 'belief_q2', 'belief_q3']
        elif self.player.round_number > 1:
            return ['belief_q3']
        else:
            print('Never see me..')


class Contribution(Page):
    form_model = 'player'
    form_fields = ['binary_choice']

    def before_next_page(self):
        # you could do this in VotingWaitPage, I just want not all the calculations to happen there
        self.player.update_privat_account()


class Voting(Page):
    def is_displayed(self):
        return self.session.config['treatment'] == 'sanction'
    form_model = 'player'
    form_fields = ['vote']

#TODO: you might have to condition here on the type of treatment which is played
class VotingWaitPage(WaitPage):
    wait_for_all_groups = True

    # when waiting for all groups this is only called once in total
    def after_all_players_arrive(self):
        for group in self.subsession.get_groups():
            group.define_bonus()
            group.set_num_giver()
            group.set_group_account()
            for player in group.get_players():
                player.set_indiv_share()
                player.calc_net_payoff()

        # TODO you could do this also earlier at voting e. g. But you have to make sure that the function is only called once
        # TODO and not one time for every group or even every player. Check if this slows down, but it really should not.
        # evalute the mode's of the binary choice and belief_q1
        if self.round_number == 1:
            self.subsession.set_frequent_binary_choice()
            self.subsession.set_frequent_binary_belief()
        else:
            self.subsession.set_frequent_binary_choice()
        # distributing the bonus for the players, when there expectations about the others were right
        # note: conditioning about the round number happens in the function
        self.subsession.set_belief_bonus()


class DecisionResults(Page):
    # initilize template variables to display on the page
    # this is needed to be able to display the variables of the other players in the group
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


class PayoffResults(Page):
    def vars_for_template(self):
        var_dic = {}
        for player in self.group.get_players():
            labelstripped = player.label.replace(' ', '')
            var_dic[labelstripped + '_indiv_share'] = player.indiv_share
            var_dic[labelstripped + '_bonus_amount'] = player.bonus_amount
            var_dic[labelstripped + '_privat_account'] = player.privat_account
            var_dic[labelstripped + '_net_payoff'] = player.net_payoff

        return var_dic

class Elicitation1(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)
    form_model = 'player'
    def get_form_fields(self):
        if self.session.config['treatment'] == 'sanction':
            return ['risk_elic']
        elif self.session.config['treatment'] == 'nosanction':
            return ['amb_elic']

class Elicitation2(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)
    form_model = 'player'
    def get_form_fields(self):
        if self.session.config['treatment'] == 'nosanction':
            return ['risk_elic']
        elif self.session.config['treatment'] == 'sanction':
            return ['amb_elic']


# so basically, for every round where you need one, one breakpoint class should do the job
class DynamicBreakPoint1(Page):
    def is_displayed(self):
        return (self.round_number == 1)
    form_model = 'player'
    form_fields = ['breakpoint1']

    def breakpoint1_error_message(self, value):
        if self.player.breakpointcounter1 == 1:
            if value != 1234:
                return "Please enter the correct code or wait until you receive the code from your instructor"
        elif self.player.breakpointcounter1 == 2:
            if value != 2468:
                return "Please enter the correct code or wait until you receive the code from your instructor"
    # TODO rethink this
    # TODO this might be an objection to have a breakpointcounter on player level
    # TODO yet, one on subsessionlevel, I would not know how to increment it only one time
    # TODO and if every player increments it or sets it, then you can actually have the variable on player level
    # TODO also, if I only let one player increment the counter on subsession level, if that tablet dies, then the other players cannot proceed
    def before_next_page(self):
        self.player.breakpointcounter1 += 1


class DynamicBreakPoint2(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)
    form_model = 'player'
    form_fields = ['breakpoint2']

    def breakpoint2_error_message(self, value):
        if self.player.breakpointcounter2 == 1:
            if value != 9988:
                return 'Please enter the correct code or wait until you receive the code from your instructor'
        elif self.player.breakpointcounter2 == 2:
            if value != 1010:
                return 'Please enter the correct code or wait until you receive the code from your instructor'
        elif self.player.breakpointcounter2 == 3:
            if value != 2018:
                return 'Please enter the correct code or wait until you receive the code from your instructor'
    # TODO: check page class before
    def before_next_page(self):
        self.player.breakpointcounter2 += 1







page_sequence = [
    Belief,
    DynamicBreakPoint1,
    Contribution,
    Voting,
    VotingWaitPage,
    DecisionResults,
    PayoffResults,
    DynamicBreakPoint1,
    DynamicBreakPoint2,
    Elicitation1,
    DynamicBreakPoint2,
    Elicitation2,
    DynamicBreakPoint2
]
