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
    players_per_group = 3 # must not be changed
    num_rounds = 7

    shilling_mult = 300
    belief_bonus = 1
    # initial value of the privat account
    ini_privat = 3
    bonus = 1
    multiplier = 2 / players_per_group
    gm_21 = [[[16, 21, 13], [5, 8, 20], [11, 17, 7], [2, 3, 1], [10, 14, 9], [15, 12, 6], [19, 4, 18]] , [[5, 9, 18], [7, 6, 16], [3, 13, 17], [15, 1, 4], [10, 12, 19], [2, 8, 21], [11, 20, 14]] , [[1, 8, 7], [14, 15, 13], [18, 12, 2], [16, 19, 20], [3, 9, 11], [17, 10, 6], [5, 4, 21]]  ,[[1, 6, 13], [15, 19, 5], [16, 2, 4], [14, 12, 7], [18, 11, 21], [17, 9, 8], [3, 10, 20]], [[15, 11, 16], [8, 10, 4], [2, 20, 13], [21, 17, 12], [18, 14, 1], [3, 7, 5], [19, 6, 9]] ,[[11, 1, 19], [8, 13, 12], [2, 9, 7], [14, 21, 3], [17, 5, 16], [6, 4, 20], [18, 10, 15]]  ,[[17, 2, 15], [13, 5, 10], [21, 7, 19], [18, 16, 3], [1, 9, 20], [14, 6, 8], [12, 11, 4]]]
    gm_18 = [[[12, 16, 6], [1, 17, 15], [2, 7, 4], [9, 14, 8], [5, 18, 3], [10, 13, 11]] ,[[4, 15, 9], [2, 11, 8], [12, 10, 1], [14, 16, 5], [18, 7, 17], [13, 6, 3]]  , [[15, 6, 2], [13, 1, 9], [8, 10, 16], [7, 5, 12], [17, 3, 14], [4, 11, 18]] ,[[1, 5, 2], [3, 9, 7], [11, 15, 12], [6, 17, 8], [18, 10, 14], [4, 13, 16]] ,[[12, 2, 3], [8, 18, 13], [14, 4, 6], [15, 10, 7], [11, 1, 16], [5, 17, 9]] , [[11, 5, 6], [15, 14, 13], [4, 10, 3], [8, 1, 7], [16, 17, 2], [18, 9, 12]], [[16, 3, 15], [5, 4, 8], [7, 14, 11], [2, 9, 10], [12, 17, 13], [1, 18, 6]] ]
    gm_15 = [[[12, 5, 6], [7, 10, 3], [15, 13, 4], [1, 11, 8], [2, 14, 9]], [[1, 5, 7], [11, 2, 4], [14, 8, 12], [13, 10, 6], [9, 3, 15]] , [[1, 15, 6], [3, 4, 5], [7, 8, 2], [14, 13, 11], [9, 12, 10]] ,[[15, 8, 10], [5, 13, 2], [9, 11, 6], [14, 3, 1], [4, 7, 12]] ,[[10, 11, 5], [8, 13, 3], [15, 12, 2], [1, 4, 9], [7, 6, 14]] ,[[13, 1, 12], [2, 6, 3], [7, 11, 15], [14, 10, 4], [5, 9, 8]] ,[[5, 15, 14], [4, 6, 8], [3, 12, 11], [10, 2, 1], [9, 13, 7]]]
    multiplier_area = 3


class Subsession(BaseSubsession):


    # put to 'off' in settings.py
    debug = models.StringField()


    # represents the numeric choice of the most players in the overall game for the contribution
    # 1: most players kept points , 2: most player gave to group account
    frequent_binary_choice = models.IntegerField()

    # represents the numeric belief of the most frequent players belief in question 2
    # 1: most players believe the other believe keeping ist best; 2: most players believe the others believe giving is best; 3: ..believe oth. bel. what others do
    frequent_binary_belief = models.IntegerField()


    def creating_session(self):

        player_num = len(self.get_players())
        # determine the total stranger matching
        # TODO if the game is played with less then 15 participants determination falls back to random shuffled groups
        for round in range(1,Constants.num_rounds+1):
            # you should be even able to play less rounds with 21,18,15 players in that implementation
            if self.round_number == round:
                if player_num == 21:
                    self.set_group_matrix(Constants.gm_21[round-1])
                elif player_num == 18:
                    self.set_group_matrix(Constants.gm_18[round-1])
                elif player_num == 15:
                    self.set_group_matrix(Constants.gm_15[round-1])
                else:
                    self.group_randomly()


        # set player labels A,B,C
        self.define_label()
        self.debug = self.session.config['debug']
        for player in self.get_players():
            player.treatment = self.session.config['treatment']

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

    # this calculates the most frequent belief of the players in round 1 from belief_q2
    # is needed to evalute the correctness of belief_q2 itself in round 1
    # 1: most player belief keeping is the correct thing; 2: most player belief giving is the correct thing 3: what others do
    def set_frequent_binary_belief(self):
        decdoc = {1:0 , 2:0, 3:0}
        for player in self.get_players():
            decdoc[player.belief_q2] += 1

        belief_list = [decdoc[1], decdoc[2], decdoc[3]]
        maxim = max(belief_list)
        occ = belief_list.count(maxim)
        # if maximum is unqiue, there is a majority belief
        if occ == 1:
            index = belief_list.index(maxim)
            self.frequent_binary_belief = index + 1
        else:
            # set to 999 if there is no most frequent belief
            self.frequent_binary_belief = 999


    # is setting q2_bonus and q3_bonus
    # doing this on subsession level so I can run it smothly after the set_frequent functions
    def set_belief_bonus(self):
            for player in self.get_players():
                if self.round_number == 1:
                    # if there was no majority belief in question 2
                    if self.frequent_binary_belief == 999:
                        player.q2_bonus = Constants.belief_bonus
                        # check if the player guessed correctly about what most of the others would actually do
                        player.q3_bonus = (player.belief_q3 == self.frequent_binary_choice) * Constants.belief_bonus
                    else:
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

    # boolean that shows if there is a majority in voting
    majority = models.BooleanField(initial=False)

    # 1:Keeper 2:Giver 3:No one , if None there is no majority
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

    # before the one shot pg the participants get 4 situations, which they have to evaluate correctly
    # their guess of the correct payoff of the left guys in picture 1
    # s1 for situation 1
    s1_group_left = models.IntegerField()
    s1_group_right = models.IntegerField()
    # number of false tries the participant had for situation1 max is 2 initial is 0
    s1_falsetries = models.IntegerField(initial=0)
    # 1 if the participant answered the situation correctly in general (after 1 or 2 tries)
    s1_correct = models.BooleanField(initial=False)

    s2_group = models.IntegerField()
    s2_falsetries = models.IntegerField(initial=0)
    s2_correct = models.BooleanField(initial=False)


    s3_group = models.IntegerField()
    s3_falsetries = models.IntegerField(initial=0)
    s3_correct = models.BooleanField(initial=False)

    s4_group_left = models.IntegerField()
    s4_group_right = models.IntegerField()
    s4_falsetries = models.IntegerField(initial=0)
    s4_correct = models.BooleanField(initial=False)



    # variables to train the participants using the tablets as first pages of the experiment
    test_number = models.IntegerField(label='')
    test_choice = models.StringField(label='',
                                      widget=widgets.RadioSelect(),
                                      choices=['A', 'B'])


    timeout_forced = models.BooleanField(initial=False)

    #tracks which breakpoint to use in oTree round 7
    breakpointcounter2 = models.IntegerField(initial=1)
    breakpoint2 = models.IntegerField(label='Enter code here:')

    # tracks which breakpoint code to use in oTree round 1
    breakpointcounter1 = models.IntegerField(initial=1)
    breakpoint1 = models.IntegerField(label='Enter code here:')

    treatment = models.StringField(choices=['sanction' , 'nosanction'])

    # this is the net payoff of one round, consists of privat account + indiv share + bonus/ in nosanction simply privat account + indiv_share
    net_payoff = models.IntegerField()

    label = models.StringField()

    privat_account = models.IntegerField(initial=Constants.ini_privat)

    # share a player gets from the group account after contribution
    indiv_share = models.IntegerField(initial=0)

    # initialize with true, defines if a player gets the bonus or if she is excluded
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
                                          [2, 'Put points to the group account?'],
                                          [3, 'Do, what others do.']],)

    belief_q2 = models.IntegerField(widget=widgets.RadioSelect(),
                                 choices=[[1,'Most player think keeping points is right.'],
                                          [2, 'Most player think giving points to group account is right.'],
                                          [3, 'Do, what others do.']],
                                 label='What do you guess most group members in this session think that one ought to do?',)

    belief_q3 = models.IntegerField(widget=widgets.RadioSelect(),
                                    choices=[[1, 'I think, most of all the players keep their points in the privat account.'],
                                             [2, 'I think, most of all the players will put their points to the group account.']],
                                    label='What do you guess most group members in this session would actually do?',
                                    )
    # bonus for answering the belief questions correct
    q2_bonus = models.IntegerField(initial=0)
    q3_bonus = models.IntegerField(initial=0)

    # coding goes as follows: the number reflects the number of hours in A, so e. g. 2 means spend 2 hours in A
    # this is for the sake of calculation
    risk_elic = models.IntegerField(widget=widgets.RadioSelect(),
                                    choices = [[0, 'Spend no hour in area A'],
                                               [1, 'Spend one hour in area A'],
                                               [2, 'Spend two hours in area A'],
                                               [3, 'Spend three hours in area A'],
                                               [4, 'Spend four hours in area A'],
                                               [5, 'Spend five hours in area A'],
                                               [6, 'Spend six hours in area A']],
                                    label = 'You have 6 hours and you can spend all in area A (where you can gain 3 points per hour spent or get nothing) or all in area B (where you get 1 point per hour spent for sure). Or you can spend some time in area A and some in B.')

    amb_elic = models.IntegerField(widget=widgets.RadioSelect(),
                                   choices=[[0, 'Spend no hour in area A'],
                                            [1, 'Spend one hour in area A'],
                                            [2, 'Spend two hours in area A'],
                                            [3, 'Spend three hours in area A'],
                                            [4, 'Spend four hours in area A'],
                                            [5, 'Spend five hours in area A'],
                                            [6, 'Spend six hours in area A']],
                                    label='You have 6 hours and you can spend all in area A (where you can gain 3 points per hour spent or get nothing) or all in area B (where you get 1 point per hour spent for sure). Or you can spend some time in area A and some in B.')

    # they payoff that results in the elic question which is payed
    elic_payoff = models.IntegerField()

    # defines which of the two elicitation questions will be payed
    elic_question_payed = models.StringField(label = 'Admin, please select which of the questions will be payed',
                                     choices=['risk', 'ambiguity'])


    # 1 if area A is good in the risk elic or amb elic question.
    # note: only one of the questions is payed, so one variable here is enough
    a_good = models.IntegerField(label='Admin, please enter if area A is good in the question which is payed.',
                                 choices=[[1,'A is good.'],
                                          [0, 'A is bad']])

    round_payed = models.IntegerField(label='Admin, please choose the number of the die, the player rolled.',
                                    choices=[1,2,3,4,5,6])


    gross_payoff = models.IntegerField()


    # note the function only calculates the payoff of the elic question which is actually payed
    # so no redundant data storage happens
    def calc_elic_payoff(self):
        if self.elic_question_payed == 'risk':
            if self.a_good == 1:
                self.elic_payoff = self.risk_elic * Constants.multiplier_area + (6 - self.risk_elic)
            elif self.a_good == 0:
                self.elic_payoff = 6 - self.risk_elic
        elif self.elic_question_payed == 'ambiguity':
            if self.a_good == 1:
                self.elic_payoff = self.amb_elic * Constants.multiplier_area + (6 - self.amb_elic)
            elif self.a_good == 0:
                self.elic_payoff = 6 - self.amb_elic


    def update_privat_account(self):
        if self.binary_choice == 2:
            self.privat_account = 0

    def set_indiv_share(self):
        self.indiv_share = Constants.multiplier * self.group.group_account


    # see variable note
    def calc_net_payoff(self):
        if self.treatment == 'sanction':
            self.net_payoff = self.privat_account + self.indiv_share + self.bonus_amount
            # there is no bonus in the nosanction treatment
        elif self.treatment == 'nosanction':
            self.net_payoff = self.privat_account + self.indiv_share

    # you dont need to condition on treatment here because this in done in calc_net_payoff
    def calc_gross_payoff(self):
        instance_in_os = self.in_round(1)
        instance_in_rx = self.in_round(self.round_payed+1)
        points_os = instance_in_os.net_payoff
        belief_points_os = instance_in_os.q2_bonus + instance_in_os.q3_bonus

        points_rx = instance_in_rx.net_payoff
        belief_points_rx = instance_in_rx.q3_bonus

        self.gross_payoff = points_os + belief_points_os + points_rx + belief_points_rx + self.elic_payoff



        ####### Questionaire variables #######

    age = models.PositiveIntegerField(
        min=18,
        max=120,
        label="How old are you?",
        doc="We collect age data, between 0 and +120.",
    )

    gender = models.CharField(
        choices=['Male', 'Female', 'Other'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="What is your gender?"
    )

    fishyears = models.CharField(
        choices=['This year only', '2 to 4', '6 to 10', '11 or more', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="How many years have you been a fisher?"
    )

    whyfish = models.CharField(
        choices=['It was the best option', 'It was the only option', 'Family tradition', 'no answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Why did you become a fisher?"
    )

    closesite = models.CharField(
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Have you always lived close to this landing site?"
    )

    moveduration = models.CharField(
        choices=['This year only', '2 to 4', '6 to 10', '11 or more', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="How many years have you lived close to this landing site?"
    )

    movefreq = models.CharField(
        choices=['Never moved', 'Once', 'A few times', 'Once a year', 'Several times a year', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="If you have moved, how often have you moved?"
    )

    moveloc = models.CharField(
        choices=['A nearby city', 'A different landing site on Lake Victoria', 'Outside of Tanzania'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="If you have moved, where did you live last year?"
    )

    parentshere = models.CharField(
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Have your parents always lived close to this landing site?",
    )

    parentsfisher = models.CharField(
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='Have your parents always been fishers?',
    )

    targetspecies = models.CharField(
        choices=['Dagaa', 'Perch/Tilapia', 'Other fish', 'All fish', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Do you target Dagaa or Nile Perch or other fish?",
    )

    targetspeciesswitch = models.CharField(
        choices=['No switch', 'Once, from Dagaa to Perch', 'Once, from Perch to Dagaa', 'Several times', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Have you switched your target fish?",
    )

    maingear = models.CharField(
        choices=['Gillnet', 'Hook', 'Dagaa net', 'Beach seine', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Which gear do you use?",
    )

    role = models.CharField(
        choices=['Owner', 'Skipper', 'Crew', 'No answer'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="What is your role on board?",
    )

    crewsize = models.IntegerField(
        min=1,
        max=20,
        widget=widgets.Slider(attrs={'step': '1'}),
        label='How many people are on board your vessel including yourself?',
    )

    complya = models.CharField(
        choices=['Almost all comply', 'Most comply', 'Many comply', 'Few comply', 'Almost no one complies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='Gillnet meshsize is above 5 inches.',
    )
    complyb = models.CharField(
        choices=['Almost all comply', 'Most comply', 'Many comply', 'Few comply', 'Almost no one complies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Dagaa net meshsize is above 10 mm.",
    )
    complyc = models.CharField(
        choices=['Almost all comply', 'Most comply', 'Many comply', 'Few comply', 'Almost no one complies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="Vessels have proper licenses.",
    )
    complyd = models.CharField(
        choices=['Almost all comply', 'Most comply', 'Many comply', 'Few comply', 'Almost no one complies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="No undersized fish are landed.",
    )

    complye = models.CharField(
        choices=['Almost all comply', 'Most comply', 'Many comply', 'Few comply', 'Almost no one complies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="No dynamite or poison is being used.",
    )

    complyother = models.CharField(
        choices=['More compliance', 'Less compliance', 'About the same'],
        widget=widgets.RadioSelect(),
        blank=True,
        label="How is the situation in other areas?",
    )

    freqmonitor = models.CharField(
        choices=['Never', 'Once or twice', 'Once a year', 'Once a month', 'More often'],
        widget=widgets.RadioSelectHorizontal(),
        blank=True,
        label='How often have you been controlled?',
    )
    fineknow = models.CharField(
        choices=['Yes', 'No'],
        widget=widgets.RadioSelectHorizontal(),
        blank=True,
        label='Do you know the level of a fine if caught violating?',
    )
    finelevel = models.CharField(
        choices=['50.000 TZS', '150 000 TZS', '300 000 TZS', '500 000 TZS', 'More than 500 000 TZS'],
        widget=widgets.RadioSelectHorizontal(),
        blank=True,
        label='What is the level of the fine?',
    )

    finelevelestimate = models.CharField(
        choices=['50.000 TZS', '150 000 TZS', '300 000 TZS', '500 000 TZS', 'More than 500 000 TZS'],
        widget=widgets.RadioSelectHorizontal(),
        blank=True,
        label='What do you think that the level of the fine is?',
    )
    manchallenge = models.CharField(
        choices=['Unsustainable practices', 'Increased effort and capactity', 'Eutrophication'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='What do you consider to be a major challenge facing fisheries in your area?',
    )

    manunsusprac = models.CharField(
        choices=['Use of beach seine', 'Use of monofilament nets', 'Use of small sized nets', 'Use of chemicals'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='If unsustainable fishing practices are used, what is the most common practice in your area?',
    )
    manunsuspeople = models.CharField(
        choices=['They are rich fishers', 'They are poor fishers', 'All are involved'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='What is your view about those engaged in unsustainable practices in your area',
    )
    manoption = models.CharField(
        choices=['Continuing with patrols', 'Regulation on quanitity of fish catch by a fisher',
                 'Regulation on number of boats and gears owned by a fisher',
                 'Giving fishing community power to control acces', 'Provision of eduation fo fishers',
                 'Control/treat effluents emission to the lake'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='What do you consider approriate options for adressing the challenge mentioned above',
    )

    manresponsibility = models.CharField(
        choices=['The state', 'BMU', 'State and BMU jointly', 'Fish processing industries', 'Civil societies'],
        widget=widgets.RadioSelect(),
        blank=True,
        label='In your opinion, who have more responsibilities in fisheries management in your area?',
    )

    manbmuchal = models.CharField(
        label='Do you think the BMU as currently constituted can adress challenges facing the fisheries in your area?',
        blank=True,
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect
    )

    manbmuperformance = models.CharField(
        label='Are you satisfied with the performance of your representative in the BMU committee in your area',
        blank=True,
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect
    )

    manbmupreference = models.CharField(
        label='If given the chance to strengthen the BMU, what do you prefer most?',
        blank=True,
        choices=['Reduce committee membership', 'Give them more responsibility', 'Financial sustainability',
                 'Improve interatcion with other stakeholders'],
        widget=widgets.RadioSelect
    )

    ecohhpeople = models.CharField(
        label='How many people are in your household?',
        blank=True,
        choices=['1', '2', '3-5', '6-10', '11-15', 'more than 15'],
        widget=widgets.RadioSelectHorizontal
    )

    ecohhearn = models.CharField(
        label='How many people earn money or provide food in your household?',
        blank=True,
        choices=['1', '2', '3-5', '6-10', '11-15', 'more than 15'],
        widget=widgets.RadioSelect
    )

    ecohhfracfish = models.CharField(
        label='Which fraction of the total income in your household comes from fishing?',
        blank=True,
        choices=['1-25%', '25-50%', '50-75%', '75-100%'],
        widget=widgets.RadioSelect
    )
    compare = models.CharField(
        label='Compared to what you consider normal, was this a good fishing season so far?',
        blank=True,
        choices=['Very good', 'Good', 'Average', 'Bad', 'Very bad', 'No answer'],
        widget=widgets.RadioSelect
    )
    earngood = models.IntegerField(
        label='On a good day:',
        blank=True,
        min=0,
        max=10000000
    )
    earnnormal = models.IntegerField(
        label='On a normal day:',
        blank=True,
        min=0,
        max=10000000
    )
    earnbad = models.IntegerField(
        label='On a bad day:',
        blank=True,
        min=0,
        max=10000000
    )
    catchgood = models.IntegerField(
        label='On a good day:',
        blank=True,
        min=0,
        max=10000000
    )
    catchnormal = models.IntegerField(
        label='On a normal day:',
        blank=True,
        min=0,
        max=10000000
    )
    catchbad = models.IntegerField(
        label='On a bad day:',
        blank=True,
        min=0,
        max=10000000
    )
    howpast = models.CharField(
        label='How does a normal fishing trip today compare to a trip last year?',
        blank=True,
        choices=['It has improved', 'It has stayed the same', 'It has worsened'],
        widget=widgets.RadioSelect
    )

    howfuture = models.CharField(
        label='How do you think a normal fishing trip today will compare to a trip next year?',
        blank=True,
        choices=['It will improve', 'It will stay the same', 'It will worsen'],
        widget=widgets.RadioSelect
    )

    futurefish = models.CharField(
        label='Do you see yourself being a fisher in 2 years time?',
        blank=True,
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect
    )
    risk = models.CharField(
        label='Generally speaking, are you a person who is willing to take risks?',
        blank=True,
        choices=['1, Not willing to take risks', '2', '3', '4', '5', '6, Very willing to take risks'],
        widget=widgets.RadioSelectHorizontal
    )
    exper = models.CharField(
        label='Have you participated in the NATCOOP survey before?',
        blank=True,
        choices=['Yes', 'No', 'No answer'],
        widget=widgets.RadioSelect
    )

    whomonitor_fish = models.BooleanField(initial=False, label="Fishers/BMU", blank=True, widget = widgets.CheckboxInput)
    whomonitor_police = models.BooleanField(initial=False, label="Police/Military", blank=True, widget = widgets.CheckboxInput)
    whomonitor_officer = models.BooleanField(initial=False, label="Fisheries officer", blank=True, widget = widgets.CheckboxInput)
    whomonitor_noone = models.BooleanField(initial=False, label="No one", blank=True, widget = widgets.CheckboxInput)

    test_risk_1 = models.CharField(
        label='What will happen to the points in area A?',
        blank=False,
        choices=['They will triple','They will be lost', 'They will stay the same'],
        widget=widgets.RadioSelect

    )

    test_risk_2 = models.CharField(
        label='What will happen to the points in area B?',
        blank=False,
        choices=['They will triple', 'They will be lost', 'They will stay the same'],
        widget=widgets.RadioSelect

    )

    test_amb_1 = models.CharField(
        label='What will happen to the points in area A?',
        blank=False,
        choices=['They will triple', 'They will be lost', 'They will stay the same'],
        widget=widgets.RadioSelect

    )

    test_amb_2 = models.CharField(
        label='What will happen to the points in area B?',
        blank=False,
        choices=['They will triple', 'They will be lost', 'They will stay the same'],
        widget=widgets.RadioSelect

    )

    study = models.CharField(
        label='What is your main field of study?',
        blank=False
    )