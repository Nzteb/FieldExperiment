from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django import forms
from django.forms import widgets as widgets2


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'testingpictures'
    players_per_group = None
    num_rounds = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    belief_q1 = models.IntegerField(widget=widgets.RadioSelect(),
                                    label='What do you think is the right thing one ought to do?',
                                    choices=[[1, 'Keep points in the private account'],
                                             [2, 'Put points to the group account?'],
                                             [3, 'Do, what others do.']], )



    whomonitor = forms.MultipleChoiceField(
        choices=['Police/military', 'Fisheries officers', 'BMU/fishers', 'No one'],
        widget=widgets2.CheckboxSelectMultiple(),
        label="Who monitors compliance in your area?",
    )





    pass
