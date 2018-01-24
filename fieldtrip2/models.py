from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'fieldtrip2'
    players_per_group = 3
    num_rounds = 3

    # initial value of the privat account
    belief_bonus = 1
    ini_privat = 3
    bonus = 3
    multiplier = 2 / players_per_group



class Subsession(BaseSubsession):

    # put to 'off' in settings.py
    debug = models.StringField()


    # represents the numeric choice of the most players in the overall game for the contribution
    # 1: most players kept points , 2: most player gave to group account
    frequent_binary_choice = models.IntegerField()

    #represents the numeric belief of the most players about what is right to do
    # 1: most players believe keeping is best; 2: most players believe giving is best
    frequent_binary_belief = models.IntegerField()


    def creating_session(self):

        self.debug = self.session.config['debug']

        # TODO implement total stranger matching for all possible group sizes which are relevant
        self.group_randomly()

        # set player labels A,B,C
        self.define_label()

    # this calculates the most frequent choice in the binary decision
    # is needed, to determine the correctness of belief_q3
    # 1: keep points 2: give to group account
    def set_frequent_binary_choice(self):
        # 1: keep points , 2: give to group account
        decdoc = {1: 0 , 2: 0}
        for player in self.get_players():
            decdoc[player.binary_choice] += 1
        # overall number of players is odd, so this is fine
        if decdoc[1] > decdoc[2]:
            self.frequent_binary_choice = 1
        else:
            self.frequent_binary_choice = 2

     # this calculates the most frequent belief of the players in round 1 from belief_q1 about which decision is correct
     # is needed to evalute the correctness of belief_q2 in round 1
     # 1: most player belief keeping is the correct thing; 2: most player belief giving is the correct thing
    def set_frequent_binary_belief(self):
        decdoc = {1:0 , 2:0}
        for player in self.get_players():
            decdoc[player.belief_q1] += 1
        # overall number of players is odd, so this is fine
        if decdoc[1] > decdoc[2]:
            self.frequent_binary_belief = 1
        else:
            self.frequent_binary_belief = 2


    # is setting q2_bonus and q3_bonus
    # doing this on subsesstion level so I can run it smothly after the set_frequent functions
    # might consider doing it on group or player level also
    def set_belief_bonus(self):
            for player in self.get_players():
                if self.round_number == 1:
                    # check if the player guessed correctly about what most of the others think is right
                    player.q2_bonus = (player.belief_q2 == self.frequent_binary_belief) * Constants.belief_bonus
                    # check if the player guessed correctly about what most of the others would actually do
                    player.q3_bonus = (player.belief_q3 == self.frequent_binary_choice) * Constants.belief_bonus
                else:
                    player.q3_bonus = (player.belief_q3 == self.frequent_binary_choice) * Constants.belief_bonus


    def define_label(self):
        matchdic = {1: 'Player A', 2: 'Player B', 3: 'Player C'}
        for group in self.get_group_matrix():
            for player in group:
                player.label = matchdic[player.id_in_group]





class Group(BaseGroup):

    group_account = models.IntegerField(initial=0)
    num_giver = models.IntegerField(initial=0)
    majority = models.BooleanField(initial=False)

    # 1:Keeper 2:Giver 3:No one
    majority_type = models.IntegerField()


    def set_num_giver(self):
        count_givers = 0
        for player in self.get_players():
            if player.binary_choice == 2:
                count_givers += 1
        self.num_giver = count_givers


    def set_group_account(self):
        self.group_account = self.num_giver * Constants.ini_privat


    # TODO: note: this function depends on 3 voting decisions, is not flexible to change in game design
    # TODO: it is also not flexible against the number of players per group
    # check for majority and determine who gets bonus
    def define_bonus(self):
        # votes coding according to player vars: 1: keeper, 2:giver , 3:no one
        votesdic = {1:0, 2:0 , 3:0}
        for player in self.get_players():
            votesdic[player.vote] += 1

        # check for majority
        for dec in votesdic.keys():
            if votesdic[dec] > 1: #TODO only works for 3 players per group
                self.majority = True
                self.majority_type = dec
                break

        # determine which of the players will get no bonus (per default all get bonus)
        if self.majority and self.majority_type != 3:
            for player in self.get_players():
                if player.binary_choice == self.majority_type:
                    player.gets_bonus = False
                    player.bonus_amount = 0




class Player(BasePlayer):

    # this is the net payoff of one round, consists of group share + indiv share + bonus
    net_payoff = models.IntegerField()


    label = models.StringField()

    privat_account = models.IntegerField(initial=Constants.ini_privat)

    indiv_share = models.IntegerField(initial=0)


    # initialize with true
    gets_bonus = models.BooleanField(initial=True)
    # initialize bonus amount with the bonus, will be set to 0 if there is a voting decision against the player type
    bonus_amount = models.IntegerField(initial=Constants.bonus)

    binary_choice = models.IntegerField(widget=widgets.RadioSelect(),
                                        label='You can either keep your %s Points or put them in the group account.' % (Constants.ini_privat),
                                        choices = [[1, 'Keep points.' ],
                                                   [2, 'Put points in account.']])

    vote = models.IntegerField(widget=widgets.RadioSelect(),
                                      verbose_name='Which players in your group you want to exclude from the bonus of %s points?' % (Constants.bonus),
                                      choices=[[1, 'The players who have kept their %s.' % (Constants.ini_privat)],
                                               [2, 'The players who put in.'],
                                               [3, 'No one.']])

    belief_q1 = models.IntegerField(widget=widgets.RadioSelect(),
                                 label='What do you think is the right thing one ought to do?',
                                 choices=[[1, 'Keep points in the private account'],
                                          [2, 'Put points to the group account?']],)

    belief_q2 = models.IntegerField(widget=widgets.RadioSelect(),
                                 choices=[[1,'Most player think keeping points is right.'],
                                          [2, 'Most player think giving points to group account is right.']],
                                 label='What do you guess most group members in this session think that one ought to do?',)

    belief_q3 = models.IntegerField(widget=widgets.RadioSelect(),
                                    choices=[[1, 'I think, most of all the players keep their points in the privat account.'],
                                             [2, 'I think, most of all the players will put their points to the group account.']],
                                    label='What do you guess most group members in this session would actually do?',
                                    )



    q2_bonus = models.IntegerField(initial=0)
    q3_bonus = models.IntegerField(initial=0)





    def update_privat_account(self):
        if self.binary_choice == 2:
            self.privat_account = 0

    def set_indiv_share(self):
        self.indiv_share = Constants.multiplier * self.group.group_account


    # see variable note
    def calc_net_payoff(self):
        self.net_payoff = self.privat_account + self.indiv_share + self.bonus_amount
