"""Collection of helper functions which are needed for drafting agents or simulation functions
"""

import cvxpy
import pandas as pd
import numpy as np
from unidecode import unidecode
import re
import itertools
from scipy.stats import norm

def cleanup_name_str(x):
    """Cleans up names from our player data file to official records 

    """
    x = unidecode(x) #gets rid of special characters and such
    #the first few here are probability not needed
    if x == 'Robert Williams':
        return 'Robert Williams III'
    if x == 'OG Anunoby':
        return 'O.G. Anunoby'
    if x == 'Marcus Morris':
        return 'Marcus Morris Sr.'
    if x == 'Alekesej Pokusevski':
        return 'Aleksej Pokusevski'
    if x == 'Pooh Jeter':
        return 'Eugene Jeter'
    if x == 'Nicolas Claxton':
        return 'Nic Claxton'
    if x == 'Richard Manning':
        return 'Rich Manning'
    if x== 'Xavier Tillman Sr.':
        return 'Xavier Tillman'
                   
    return x

def setup(season):
    """Prepares a stat dataframe and a position series for a season"""

    season_str = str(season - 1) + '-' + str(season)[2:]
    stat_df = pd.read_csv('../data/stat_data/' + season_str + '_complete.csv')\
            [['PLAYER_ID','PTS','REB','AST','STL','BLK','FG3M','TO','FGM','FGA','FTM','FTA','date']]
    stat_df.columns = ['id','pts','trb','ast','stl','blk','fg3','tov','fg','fga','ft','fta','date']

    player_df = pd.read_csv('../data/player_id_reference.csv')
    position_df = pd.read_csv('../data/positions.csv')

    essential_info = stat_df.merge(player_df[['id','player']])

    position_df = position_df[position_df['season'] == season] 
    positions = position_df.set_index(['player'])['pos']
    
    essential_info['date'] = pd.to_datetime(essential_info['date'])
    essential_info['week'] = essential_info['date'].dt.isocalendar()['week']

    #make sure we aren't missing any weeks when a player didn't play
    weekly_df_index = pd.MultiIndex.from_product([pd.unique(essential_info['player'])
                                                 ,pd.unique(essential_info['week'])]
                                                 ,names = ['player','week'])
    weekly_df = essential_info.drop(columns = ['date','id']).groupby(['player','week']).sum()
    season_df = pd.DataFrame(weekly_df, index = weekly_df_index ).fillna(0)
    
    return season_df, positions

def check_team_eligibility(players):    
    """Checks if a team is eligible or not, based on the players' possible positions

    The function works by setting up an optimization problem for assigning players to team positions
    If the optimization problem is infeasible, the team is not eligible
    
    Args:
        players:Lists of players, which are themselves lists of eligible positions. E.g. 
                [['SF','PF'],['C'],['SF']]

    Returns:
        True or False, depending on if the team is found to be eligible or not

    """
    n_players = len(players)
    
    #we need 8 columns for the 8 positions. We are defining them as 
    #C, PG, SG, G, SF, PF, F, U 
    X = cvxpy.Variable(shape = (n_players,8)) #we could set boolean = True, but it takes much longer

    eligibility = np.concatenate([get_eligibility_row(player) for player in players])
    #each player gets 1 position
    one_position_constraint = cvxpy.sum(X,axis = 1) == 1
    
    #total number of players in each category cannot exceed the maximum for the category
    available_positions_constraint = cvxpy.sum(X,axis = 0) <= [2,1,1,2,1,1,2,3]    
    
    #players can only play at positions they are eligible for 
    eligibility_constraint = X <= eligibility 
    
    positivity_constraint = X >= 0
    
    constraints = [one_position_constraint, available_positions_constraint, eligibility_constraint, positivity_constraint]
    problem = cvxpy.Problem(cvxpy.Minimize(0), constraints)
    problem.solve()
            
    return not problem.status == "infeasible"

def get_eligibility_row(pos):
    """Converts a list of player positions into a binary vector of length 8, for the 8 team positions"""
    eligibility = {7}
    if 'C' in pos:
        eligibility.add(0)
    if 'PG' in pos: 
        eligibility.update((1,3))
    if 'SG' in pos: 
        eligibility.update((2,3))
    if 'SF' in pos: 
        eligibility.update((4,6))
    if 'PF' in pos: 
        eligibility.update((5,6))
    return np.array([[i in eligibility for i in range(8)]])


#this recursive function allows us to enumerate the winning probabilities efficiently
#it allows the drafter to work ~5 times faster than it would with a list comprehension for the same step 
def combinatorial_calculation(c
                              , c_comp
                              , categories
                              , data = 1 #the latest probabilities. Defaults to 1 at start
                              , level = 0 #the number of categories that have been worked into the probability
                              , n_false = 0 #the number of category losses that have been trackes so far
                             ):
    """This recursive functions enumerates winning probabilities for the Gaussian optimizer

    The function's recursive structure creates a binary tree, where each split is based on whether the next category is 
    won or lost. At the high level it looks like 
    
                                            (start) 
                                    |                   |
                                won rebounds      lost rebounds
                             |          |           |            |
                          won pts    lost pts   won pts     lost pts
                          
    The probabilities of winning scenarios are then added along the tree. This is more efficient than brute force calculation
    of each possibility, because it doesn't repeat multiplication steps for similar scenarios like (won 9) and (won 8 then 
    lost the last 1). Ultimately it is about five times faster than the equivalent with list comprehension
    
    Args:
        c: Dataframe of all category winning probabilities. One column per category, one row per player
        c_comp: 1 - c
        categories: list of the relevant categories
        data: probability of the node's scenario. Defaults to 1 because no categories are required at first
        level: the number of categories that have been worked into the probability
        n_false: the number of category losses that have been tracked so far. When it gets high enough 
                 we write off the node; the remaining scenarios do not contribute to winning chances

    Returns:
        Probability of winning a majority of categories for each player 

    """
    if n_false > (len(categories) -1)/2: #scenarios where a majority of categories are losses are overall losses
        return 0 
    elif level < len(categories):
        #find the total winning probability of both branches from this point- if we win or lose the current category 
        return combinatorial_calculation(c, c_comp, categories, data * c[categories[level]], level + 1, n_false) + \
                combinatorial_calculation(c, c_comp, categories, data * c_comp[categories[level]], level + 1, n_false + 1)
    else: #a series where all 9 categories has been processed, and n_false <= the cutoff, can be added to the total %
        return data


def calculate_coefficients(season_df
                     , representative_player_set):
    """calculate the coefficients for each category- \mu,\sigma, and \tau, so we can use them for Z-scores and G-scores """

    main_categories = ['pts', 'trb', 'ast', 'stl', 'blk', 'fg3','tov']
    player_stats = season_df.groupby(level = 'player').agg(['mean','var'])

    #counting stats
    mean_of_vars = player_stats.loc[representative_player_set,(main_categories,'var')].mean(axis = 0)
    var_of_means = player_stats.loc[representative_player_set,(main_categories,'mean')].var(axis = 0)
    mean_of_means = player_stats.loc[representative_player_set,(main_categories,'mean')].mean(axis = 0)

    #free throw percent
    ft_mean_of_means = player_stats.loc[representative_player_set, ('ft','mean')].mean()
    fta_mean_of_means = player_stats.loc[representative_player_set, ('fta','mean')].mean()
    mean_of_means.loc['fta'] = fta_mean_of_means
    ftp = player_stats.loc[:, ('ft','mean')]/player_stats.loc[:, ('fta','mean')]
    ftp_agg_average = ft_mean_of_means / fta_mean_of_means
    mean_of_means.loc['ft_pct'] = ftp_agg_average
    ftp_numerator = player_stats.loc[:, ('fta','mean')]/fta_mean_of_means * (ftp - ftp_agg_average)
    ftp_var_of_means = ftp_numerator.loc[representative_player_set].var()
    var_of_means.loc['ft_pct'] = ftp_var_of_means
    
    season_df.loc[:,'volume_adjusted_ftp'] = (season_df['ft'] - season_df['fta']*ftp_agg_average)/ \
                                            fta_mean_of_means
    ftp_mean_of_vars = season_df['volume_adjusted_ftp'].loc[representative_player_set].groupby('player').var().mean()
    mean_of_vars.loc['ft_pct'] = ftp_mean_of_vars

    #field goal percent
    fg_mean_of_means = player_stats.loc[representative_player_set, ('fg','mean')].mean()
    fga_mean_of_means = player_stats.loc[representative_player_set, ('fga','mean')].mean()
    mean_of_means.loc['fga'] = fga_mean_of_means
    fgp_agg_average = fg_mean_of_means / fga_mean_of_means
    mean_of_means.loc['fg_pct'] = fgp_agg_average
    fgp = player_stats.loc[:, ('fg','mean')]/player_stats.loc[:, ('fga','mean')]
    fgp_numerator = player_stats.loc[:, ('fga','mean')]/fga_mean_of_means * (fgp - fgp_agg_average)
    fgp_var_of_means = fgp_numerator.loc[representative_player_set].var()
    var_of_means.loc['fg_pct'] = fgp_var_of_means
    season_df.loc[:,'volume_adjusted_fgp'] = (season_df['fg'] - season_df['fga']*fgp_agg_average)/ \
                                        fga_mean_of_means
    fgp_mean_of_vars = season_df['volume_adjusted_fgp'].loc[representative_player_set].groupby('player').var().mean()    
    mean_of_vars.loc['fg_pct'] = fgp_mean_of_vars
        
    return mean_of_means.droplevel(1), var_of_means.droplevel(1), mean_of_vars.droplevel(1)

def calculate_scores_from_coefficients(season_df
                                       ,mean_of_means
                                       ,var_of_means
                                       ,mean_of_vars
                                       ,alpha_weight = 1
                                       ,beta_weight = 1):
    """Calculate scores based on player info and coefficients. alpha_weight is for \sigma, beta_weight is for \tau"""
    
    main_categories = ['pts', 'trb', 'ast', 'stl', 'blk', 'fg3','tov']
    player_stats = season_df.groupby(level = 'player').mean()

    main_cat_mean_of_means = mean_of_means.loc[main_categories]
    main_cat_var_of_means = var_of_means.loc[main_categories]
    main_cat_mean_of_vars = mean_of_vars.loc[main_categories]

    main_cat_denominator = (main_cat_var_of_means.values*alpha_weight + main_cat_mean_of_vars.values*beta_weight ) ** 0.5
    numerator = player_stats.loc[:,main_categories] - main_cat_mean_of_means
    main_scores = numerator.divide(main_cat_denominator)
    main_scores['tov'] = - main_scores['tov']

    #free throws 
    ftp = player_stats.loc[:, 'ft']/player_stats.loc[:, 'fta']
    ftp_denominator = (var_of_means['ft_pct']*alpha_weight + mean_of_vars['ft_pct']*beta_weight)**0.5
    ftp_numerator = player_stats.loc[:, 'fta']/mean_of_means['fta'] * (ftp - mean_of_means['ft_pct'])
    ftp_score = ftp_numerator.divide(ftp_denominator)

    #field goals
    fgp = player_stats.loc[:, 'fg']/player_stats.loc[:, 'fga']
    fgp_denominator = (var_of_means['fg_pct']*alpha_weight + mean_of_vars['fg_pct']*beta_weight)**0.5
    fgp_numerator = player_stats.loc[:, 'fga']/mean_of_means['fga'] * (fgp - mean_of_means['fg_pct'])
    fgp_score = fgp_numerator.divide(fgp_denominator)
    
    res = pd.concat([main_scores, ftp_score, fgp_score],axis = 1)  
    res.columns = ['pts', 'trb', 'ast', 'stl', 'blk', 'fg3','tov', 'ft_pct','fg_pct']
    return res
    
def round_robin_opponent(t
                         , w
                         , n =12): 
    """Calculates the opposing team number based on a round robin schedule

    Based on the circle method as defined by wikipedia
    https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method
    
    Args:
        t: team number, from 0
        w: week number, from 0
        n: number of teams - must be an even number
        
    Returns:
        The opposing team number for team t during week w
    """
    if t == 0: #position 0 remains fixed, and the other teams rotate around their (n - 1) spots
        return ((n - 2 - w) % (n - 1) ) + 1
    elif ((t + w) % (n-1) ==0): # in spot (n-1) of the non-zero spots, the opponent is 0 
        return 0 
    else: #we calculate the current position of team, infer the opponent's position, then calculate the opposing team
        res = (((n - 1 - (t + w) % (n - 1)) % (n - 1))- w) % (n - 1)
        return (n - 1) if res == 0 else res