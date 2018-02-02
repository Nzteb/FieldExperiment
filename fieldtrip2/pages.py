from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


# let the participants train how to use a tablet
class TestingParticipant(Page):
    def is_displayed(self):
        return (self.round_number == 1)

    def test_number_error_message(self, value):
        if value != 20:
            return 'Please enter the number 20.'

    def test_choice_error_message(self, value):
        if value != 'A':
            return 'Please choose picture A.'

    def test_slider_error_message(self, value):
        if value != 7:
            return 'Please choose the value 5'

    form_model = 'player'
    form_fields = ['test_number', 'test_choice', 'test_slider']



class Situation1(Page):
    def is_displayed(self):
        return (self.round_number == 1)

    form_model = 'player'
    form_fields = ['s1_group_left' , 's1_group_right']

    def error_message(self, values):
        if values['s1_group_left'] != 2 or values['s1_group_right'] != 5:
            if self.player.s1_tryagain == False:
                self.player.s1_tryagain = True
                return 'Please try again'
            else:
                pass  # as it is the 2nd try of the player, let him pass the page anyway

class Solution1(Page):
    def is_displayed(self):
        return (self.round_number == 1)


class Situation2(Page):
    def is_displayed(self):
        return (self.round_number == 1)

    form_model = 'player'
    form_fields = ['s2_group']

    def s2_group_error_message(self, value):
        if value != 3:
            if self.player.s2_tryagain == False:
                self.player.s2_tryagain = True
                return 'Please try again.'
            else:
                pass #let him pass anyway as it is second try

class Solution2(Page):
    def is_displayed(self):
        return (self.round_number == 1)


class Situation3(Page):
    def is_displayed(self):
        return (self.round_number == 1)

    form_model = 'player'
    form_fields = ['s3_group']

    def s3_group_error_message(self, value):
        if value != 6:
            if self.player.s3_tryagain == False:
                self.player.s3_tryagain = True
                return 'Please try again.'
            else:
                pass #pass anyway

class Solution3(Page):
    def is_displayed(self):
        return (self.round_number == 1)



class Situation4(Page):
    def is_displayed(self):
        return (self.round_number == 1)

    form_model = 'player'
    form_fields = ['s4_group_left', 's4_group_right']

    def error_message(self, values):
        if values['s4_group_left'] != 4 or values['s4_group_right'] != 7:
            if self.player.s4_tryagain == False:
                self.player.s4_tryagain = True
                return 'Please try again'
            else:
                pass  # as it is the 2nd try of the player, let him pass the page anyway

class Solution4(Page):
    def is_displayed(self):
        return (self.round_number == 1)


class Belief1(Page):
    def is_displayed(self):
        return (self.round_number == 1)
    form_model = 'player'
    form_fields = ['belief_q1']

class Belief2(Page):
    def is_displayed(self):
        return (self.round_number == 1)
    form_model = 'player'
    form_fields = ['belief_q2']

class Belief3(Page):
    form_model = 'player'
    form_fields = ['belief_q3']




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
class BeforeResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    # when waiting for all groups this is only called once in total
    def after_all_players_arrive(self):
        for group in self.subsession.get_groups():
            # bonus only in sanction treatment
            if self.session.config['treatment'] == 'sanction':
                group.define_bonus()
            group.set_num_giver()
            group.set_group_account()
            for player in group.get_players():
                player.set_indiv_share()
                # conditioning for treatment happens in the calc_net function already
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



class Results1 (Page):
    def vars_for_template(self):
        # save the player objects in a dic to be able to identify them by label
        pl_objects = {}
        for player in self.player.group.get_players():
            for label in ['Player A', 'Player B', 'Player C']:
                if player.label == label:
                    pl_objects[label] = player

        playerA = pl_objects['Player A']
        playerB = pl_objects['Player B']
        playerC = pl_objects['Player C']

        var_dic = {}

        if self.player.label == 'Player A':
            var_dic['p2_choice'] = playerB.binary_choice
            var_dic['p2_label'] = playerB.label
            var_dic['p3_choice'] = playerC.binary_choice
            var_dic['p3_label'] = playerC.label
            if self.player.treatment == 'sanction':
                var_dic['p2_bonus'] = playerB.gets_bonus
                var_dic['p3_bonus'] = playerC.gets_bonus
            return var_dic

        if self.player.label == 'Player B':
            var_dic['p2_choice'] = playerA.binary_choice
            var_dic['p2_label'] = playerA.label
            var_dic['p3_choice'] = playerC.binary_choice
            var_dic['p3_label'] = playerC.label
            if self.player.treatment == 'sanction':
                var_dic['p2_bonus'] = playerA.gets_bonus
                var_dic['p3_bonus'] = playerC.gets_bonus
            return var_dic


        if self.player.label == 'Player C':
            var_dic['p2_choice'] = playerA.binary_choice
            var_dic['p2_label'] = playerA.label
            var_dic['p3_choice'] = playerB.binary_choice
            var_dic['p3_label'] = playerB.label
            if self.player.treatment == 'sanction':
                var_dic['p2_bonus'] = playerA.gets_bonus
                var_dic['p3_bonus'] = playerB.gets_bonus
            return var_dic


class Results2 (Page):
    def vars_for_template(self):
        return {'points': self.player.indiv_share + self.player.privat_account}



#old version of the page, displays full debug tables and non ordering of the table

# class ResultsOld(Page):
#     # initilize template variables to display on the page
#     # this is needed to be able to display the variables of the other players in the group
#     # some vars here are only for debug purposes
#     def vars_for_template(self):
#         # keys of var_dic are the variable names in the template
#         var_dic = {}
#         for player in self.group.get_players():
#             labelstripped = player.label.replace(' ', '')
#
#             var_dic[labelstripped + '_choice' ] = player.binary_choice
#             var_dic[labelstripped + '_indiv_share'] = player.indiv_share
#             var_dic[labelstripped + '_privat_account'] = player.privat_account
#             var_dic[labelstripped + '_net_payoff'] = player.net_payoff
#
#             if player.treatment == 'sanction':
#                 var_dic[labelstripped + '_vote'] = player.vote
#                 var_dic[labelstripped + '_bonus'] = player.gets_bonus
#                 var_dic[labelstripped + '_bonus_amount'] = player.bonus_amount
#             else:
#                 var_dic[labelstripped + '_vote'] = 'No voting in game'
#                 var_dic[labelstripped + '_bonus'] = 'No bonus in game'
#                 var_dic[labelstripped + '_bonus_amount'] = 'No bonus in game'
#
#         return var_dic


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
        return  (self.round_number == 1)
    form_model = 'player'
    form_fields = ['breakpoint1']

    def breakpoint1_error_message(self, value):
        if self.player.breakpointcounter1 == 1:
            if value != 1234:
                return "Please enter the correct code or wait until you receive the code from your instructor"
        elif self.player.breakpointcounter1 == 2:
            if value != 2468:
                return "Please enter the correct code or wait until you receive the code from your instructor"
    # TODO actually I really like my breakpoint idea now. Because we have 6 breakpoints but only 2 classes and
    # TODO I can, dynamically, simply here and in the template add new breakpoints, without defining new variables!
    def before_next_page(self):
        self.player.breakpointcounter1 += 1
        self.player.breakpoint1 = None


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
        elif self.player.breakpointcounter2 == 4:
            if value != 4538:
                return 'Please bring the tablet to the instructor and let him enter the code.'
    def before_next_page(self):
        self.player.breakpointcounter2 += 1
        self.player.breakpoint2 = None


class AdminPage(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)
    form_model = 'player'
    form_fields = ['elic_question_payed', 'a_good', 'round_payed']

    def before_next_page(self):
        self.player.calc_elic_payoff()
        self.player.calc_gross_payoff()

class GrossPayoff(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)

    def vars_for_template(self):
        vars_dic = {}
        # for us if e. g. round 1 is payed because the dice rolls 1 then for otree this is actually round 2 because the one shot game is round 1
        round_payed = self.player.round_payed +1

        os_np = self.player.in_round(1).net_payoff
        os_q2_bonus = self.player.in_round(1).q2_bonus
        os_q3_bonus = self.player.in_round(1).q3_bonus
        sum_row1 = os_np + os_q2_bonus + os_q3_bonus

        rx_np = self.player.in_round(round_payed).net_payoff
        rx_q3_bonus = self.player.in_round(round_payed).q3_bonus
        sum_rowx = rx_np + rx_q3_bonus

        vars_dic['rp'] = round_payed - 1

        # os for one shot
        vars_dic['os_np'] = os_np
        vars_dic['os_q2_bonus'] = os_q2_bonus
        vars_dic['os_q3_bonus'] = os_q3_bonus
        vars_dic['sum_row1'] = sum_row1

        # rx for round x
        vars_dic['rx_np'] = rx_np
        vars_dic['rx_q3_bonus'] = rx_q3_bonus
        vars_dic['sum_rowx'] = sum_rowx


        #gross payoff in shilling
        vars_dic['shilling'] = self.player.gross_payoff * Constants.shilling_mult

        return vars_dic



class DBP1WaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(self):
        return (self.round_number == 1)


class DBP2WaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)


class ContributionWaitPage(WaitPage):
    wait_for_all_groups = True

class BeliefWaitPage(WaitPage):
    def is_displayed(self):
        return (self.round_number > 1)

class TestingParWaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(self):
        return (self.round_number == 1)






page_sequence = [
    TestingParticipant,
    TestingParWaitPage,
    Situation1,
    Solution1,
    Situation2,
    Solution2,
    Situation3,
    Solution3,
    Situation4,
    Solution4,
    Belief1,
    Belief2,
    Belief3,
    BeliefWaitPage, #this is for rounds >1 (in round 1 the breakpoint does the job)
    DynamicBreakPoint1,
    DBP1WaitPage,
    Contribution,
    ContributionWaitPage,
    Voting,
    BeforeResultsWaitPage,
    Results1,
    Results2,
    DynamicBreakPoint1,
    DBP1WaitPage,
    DynamicBreakPoint2,
    DBP2WaitPage,
    Elicitation1,
    DynamicBreakPoint2,
    DBP2WaitPage,
    Elicitation2,
    DynamicBreakPoint2,
    DBP2WaitPage,
    #put questionaire pages in
    DynamicBreakPoint2,
    AdminPage,
    GrossPayoff
]
