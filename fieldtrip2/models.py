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

    #initial value of the privat account
    ini_privat = 3
    bonus = 3


class Subsession(BaseSubsession):



    def creating_session(self):

        #TODO implement total stranger matching for all possible round numbers
        self.group_randomly()

        #set player labels A,B,C
        self.define_label()


    def define_label(self):
        matchdic = {1: 'Player A', 2: 'Player B', 3: 'Player C'}
        for group in self.get_group_matrix():
            for player in group:
                player.label = matchdic[player.id_in_group]





class Group(BaseGroup):

    majority = models.BooleanField(initial=False)

    #1:Keeper 2:Giver 3:No one
    majority_type = models.IntegerField()

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

    label = models.StringField()

    #initialize with true
    gets_bonus = models.BooleanField(initial=True)
    #initialize bonus amount with the bonus, will be set to 0 if there is a voting decision against the player type
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

