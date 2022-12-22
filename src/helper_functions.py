"""Collection of helper functions which are needed for drafting agents or simulation functions
"""

import cvxpy
import pandas as pd
import numpy as np

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
    available_positions_constraint = cvxpy.sum(X,axis = 0) <= [3,1,1,2,1,1,2,3]    
    
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

def process_stat_df(stat_df, categories):
    """manually add a section of the stat df for FG% and FT%, and flip turnovers """
    stat_df = pd.concat([stat_df, pd.DataFrame(columns = pd.MultiIndex.from_product([["fg_pct", "ft_pct"]
                                                                                     , ["mean", "var"]])
                                              , index = stat_df.index)], axis = 1)
                           
    stat_df.loc[:,('fg_pct','mean')] = stat_df.loc[:,('fg','mean')]/stat_df.loc[:,('fga','mean')]
    stat_df.loc[:,('fg_pct','var')] = stat_df['fg_var']/(stat_df.loc[:,('fga','mean')]**2)

    stat_df.loc[:,('ft_pct','mean')] = stat_df.loc[:,('ft','mean')]/stat_df.loc[:,('fta','mean')]
    stat_df.loc[:,('ft_pct','var')] = stat_df['ft_var']/(stat_df.loc[:,('fta','mean')]**2)
    
    stat_df.loc[:,('tov','mean')] = - stat_df.loc[:,('tov','mean')]
    stat_df = stat_df[categories]
    stat_df.sort_index(axis=1, inplace = True)
    return stat_df

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
    