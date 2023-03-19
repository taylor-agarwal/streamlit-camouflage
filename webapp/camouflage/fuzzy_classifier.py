# From https://github.com/FCARRILLOM/ClassifyingColorMatchingOutfits/blob/main/ColorMeMedium.ipynb

import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import streamlit as st

hue_fuzzy = ['WARM', 'COOL', 'WARM_']
sat_fuzzy = ['GRAY', 'VERY_FADED', 'FADED', 'SATURATED', 'VERY_SATURATED']
val_fuzzy = ['BLACK', 'VERY_DARK', 'DARK', 'BRIGHT', 'VERY_BRIGHT']
tone_fuzzy = ['NEUTRAL', 'DARK', 'BRIGHT']

@st.cache_resource
def get_tone_hue():
    """
    Antecedents HSV
    HUE: color represented by number from 0(red) - 360(violet)
    { WARM, COOL }

    SATURATION: color saturation represented by number from 0(faded/gray color) - 100(full color)
    { GRAY, VERY_FADED, FADED, SATURATED, VERY_SATURATED }

    VALUE: brightness represented by number 0(dark) - 100(light)
    { BLACK, VERY_DARK, DARK, BRIGHT, VERY_BRIGHT }
    """

    hue_range = np.arange(0, 361, 1)
    hue = ctrl.Antecedent(hue_range, 'hue')
    hue['WARM'] = fuzz.gaussmf(hue.universe, 0, 60)
    hue['COOL'] = fuzz.gaussmf(hue.universe, 180, 60)
    hue['WARM_'] = fuzz.gaussmf(hue.universe, 360, 60)


    sat = ctrl.Antecedent(np.arange(0, 101, 1), 'saturation')
    sat['GRAY'] = fuzz.gaussmf(sat.universe, 0, 10)
    sat['VERY_FADED'] = fuzz.gaussmf(sat.universe, 25, 10)
    sat['FADED'] = fuzz.gaussmf(sat.universe, 50, 10)
    sat['SATURATED'] = fuzz.gaussmf(sat.universe, 75, 10)
    sat['VERY_SATURATED'] = fuzz.gaussmf(sat.universe, 100, 10)


    val = ctrl.Antecedent(np.arange(0, 101, 1), 'value')
    val['BLACK'] = fuzz.gaussmf(val.universe, 0, 10)
    val['VERY_DARK'] = fuzz.gaussmf(val.universe, 25, 10)
    val['DARK'] = fuzz.gaussmf(val.universe, 50, 10)
    val['BRIGHT'] = fuzz.gaussmf(val.universe, 75, 10)
    val['VERY_BRIGHT'] = fuzz.gaussmf(val.universe, 100, 10)


    """
    Consequents
    TONE: mix of Saturation and Value that indicate if color is neutral or dark/bright
    { NEUTRAL, DARK, BRIGHT }
    """
    tone_range = np.arange(0, 12, 1)
    tone = ctrl.Consequent(tone_range, 'tone')
    tone['NEUTRAL'] = fuzz.trapmf(tone.universe, [0, 0, 1, 2])
    tone['DARK'] = fuzz.gbellmf(tone.universe, 2, 1, 3)
    tone['BRIGHT'] = fuzz.gbellmf(tone.universe, 4, 1, 9.5)


    """
    Fuzzy rules
    for tones
    """
    rule1 = ctrl.Rule(val['BLACK'] | sat['GRAY'] | sat['VERY_FADED'], tone['NEUTRAL'], 'Dark colors without color (low brightness/dark) considered neutral')
    rule2 = ctrl.Rule(val['VERY_DARK'] & sat['SATURATED'], tone['NEUTRAL'], 'Very dark colors with high saturation')
    rule3 = ctrl.Rule(val['DARK'] & sat['FADED'], tone['DARK'], 'Dark color with normal saturation')
    rule4 = ctrl.Rule(val['DARK'] & sat['VERY_SATURATED'], tone['BRIGHT'], 'Dark color with high saturation')
    rule5 = ctrl.Rule(val['BRIGHT'] & sat['SATURATED'], tone['BRIGHT'], 'Bright color with high saturation')
    rule6 = ctrl.Rule(val['VERY_BRIGHT'] & sat['FADED'], tone['BRIGHT'], 'Very bright color with some saturation')
    rule7 = ctrl.Rule(val['VERY_BRIGHT'] & sat['VERY_SATURATED'], tone['BRIGHT'], 'Very bright color with high saturation')
    rule8 = ctrl.Rule(val['VERY_DARK'] & sat['FADED'], tone['NEUTRAL'], 'Very dark color with faded saturation')

    """
    Control system
    for tones
    """
    tone_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])

    return tone_ctrl, tone_range, tone, hue_range, hue


tone_ctrl, tone_range, tone, hue_range, hue = get_tone_hue()

####################
## CLOTHES TYPING ##
####################

def GetMembership(fuzzy_values, var_range, var_model, crisp_value):
    """
    GetMembership
    Returns String representing the Fuzzy value given a variable's range, model, and crisp value
    """
    max_membership = 0
    membership_name = fuzzy_values[0]
    for i in range(len(fuzzy_values)):
        temp_memb = fuzz.interp_membership(var_range, var_model[fuzzy_values[i]].mf, crisp_value)
        if temp_memb > max_membership:
            max_membership = temp_memb
            membership_name = fuzzy_values[i]
    return membership_name



def GetTone(values):
    """
    Given Saturation and Value, returns a String indicating if the combination 
    of both values results in a 'NEUTRAL', 'DARK', or 'BRIGHT' tone.
    INPUT:
    values - tuple(sat, val)
        + sat - value from 0-100
        + val - value from 0-100
    """
    tone_sim = ctrl.ControlSystemSimulation(tone_ctrl)
    tone_sim.input['saturation'] = values[0]
    tone_sim.input['value'] = values[1]
    tone_sim.compute()
    tone_output = tone_sim.output['tone']
    tone_membership = GetMembership(tone_fuzzy, tone_range, tone, tone_output)
    return tone_membership



def GetColorTemp(hue_val):
    """
    Given Hue, returns a String indicating if the color belongs
    to 'WARM' or 'COOL' colors.
    INPUT:
    hue - value from 0-360
    """
    temp_membership = GetMembership(hue_fuzzy, hue_range, hue, hue_val)
    return temp_membership


def GetColorDesc(hsv):
    """
    Given Hue, Saturation, and Value, returns a String describing
    the specified color. The output is composed of both the tone of
    the color, and the temperature of the color.
    INPUT:
    hsv - tuple(hue, sat, val)
        + hue - value from 0-360
        + sat - value from 0-100
        + val - value from 0-100
    OUTPUT: (TONE, TEMP) ex. (DARK, WARM)
    """
    tone = GetTone((hsv[1], hsv[2]))
    temp = GetColorTemp(hsv[0])
    if temp == "WARM_": temp = "WARM"
    return (tone, temp)


######################
## CLOTHES MATCHING ##
######################

def BasicMatch(outfit):
    """
    Basic outfit follow these rules
    - No more than one bright color
    - No high contrast between colors (bright warm + dark cool)
    - Any number of neutral colors can fit anywhere
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT: 
        True or False
    """
    
    bright_count = len([i for i in outfit if i[0] == 'BRIGHT'])
    if bright_count > 1: return False
    # Check for high contrast
    
    return True


def NeutralMatch(outfit):
    """
    Neutral outfit follow these rules
    - Only neutral colors
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT:
        True or False
    """
    
    neutral = [color for color in outfit if color[0] == 'NEUTRAL']
    if len(neutral) != len(outfit):
        return False
    
    return True


def AnalogousMatch(outfit):
    """
    Analogous outfit follow these rules
    - All colors must be within the same temp.
    - Any number of neutral colors
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT:
        True or False
    """
    
    cool_count = len([color for color in outfit if color[1] == 'COOL'])
    warm_count = len(outfit) - cool_count
    if cool_count < len(outfit) and warm_count < len(outfit):
        return False
    
    return True


def ContrastMatch(outfit):
    """
    Contrast outfit follow these rules
    - At least one warm color
    - Both dark and bright colors present
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT:
        True or False
    """
    
    warm_count = len([color for color in outfit if color[1] == 'WARM'])
    if warm_count < 1: return False
    
    dark_count = len([color for color in outfit if color[0] == 'DARK'])
    bright_count = len([color for color in outfit if color[0] == 'BRIGHT'])
    if dark_count < 1 or bright_count < 1:
        return False
    
    return True


def SummerMatch(outfit):
    """
    Bright summer outfit follow these rules
    - At least two warm colors
    - At least one bright color
    - At most one dark color
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT: 
        True or False
    """
    
    non_neutral = [color for color in outfit if color[0] != 'NEUTRAL']
    
    warm_count = len([color for color in non_neutral if color[1] == 'WARM'])
    if warm_count < 2: return False
    
    dark_count = len([color for color in non_neutral if color[0] == 'DARK'])
    if dark_count > 1: return False
    
    bright_count = len(non_neutral) - dark_count
    if bright_count < 1: return False
    
    return True




def WinterMatch(outfit):
    """
    Dark winter outfit follow these rules
    - At least one dark color
    - No bright colors
    INPUT:
    outfit - tuple(top, bot, shs)
        top - tuple(tone, temp)
        bot - tuple(tone, temp)
        shs - tuple(tone, temp)
    OUTPUT:
        True or False
    """
    
    non_neutral = [color for color in outfit if color[0] != 'NEUTRAL']
    
    dark_count = len([color for color in non_neutral if color[0] == 'DARK'])
    if dark_count < 1: return False
    
    bright_count = len(non_neutral) - dark_count
    if bright_count > 0: return False
    
    return True



def GetValidMatches(outfit):
    """
    Iterate outfit over all color schemes and get all valid matches
    INPUT:
    outfit - tuple(top, bot, shs)
        top - hsv
        bot - hsv
        shs - hsv
    OUTPUT:
        All names of valid outfit matches
    """
    
    rules = {"Basic": BasicMatch, "Neutral": NeutralMatch,
             "Analogous": AnalogousMatch, "Contrast": ContrastMatch, # I added Contrast
             "Summer": SummerMatch, "Winter": WinterMatch}
    valid_matches = []
    for key in rules:
        if rules[key](outfit):
            valid_matches.append(key)
    return valid_matches