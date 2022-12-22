"""Definitions of the drafting agent classes
Drafting agents choose players during drafts, according to pre-set algorithms 
"""

import pandas as pd
import numpy as np
from scipy import special
from src.simulation import run_draft
from sklearn.preprocessing import StandardScaler

from src.helper_functions import check_team_eligibility, combinatorial_calculation, process_stat_df

class SimpleAgent():
    """Abstract implementation of a simple agent, which picks players according to an internal order

    Cannot be used as an actual agent, because it has no order to pick from 

    Attributes:
        players: A list of players already chosen by this agent
        positions: Eligible positions of each possible player. Agents need this info to make sure they draft eligible teams
    """
    def __init__(self, positions):
        self.players = []
        self.positions = positions
    
    def pick_from_order(self
                        , available_players):
        """Picks players from an ordered Series of available players, with a check for eligibility

        Args:
            available_players: Series of players in order of draft preference

        Returns:
            String indicating chosen player. Also internally adds player to self.players list

        """
        #every team of less than 5 players is automatically eligible
        if len(self.players) < 5:
            player = available_players.index[0]
            self.players = self.players + [player]
            return player
        else:
            for player in available_players.index:
                theoretical_team = self.players + [player]
                if check_team_eligibility(list(self.positions.loc[theoretical_team])):
                    self.players = theoretical_team
                    return player
            raise ValueError('No available players!')

    def make_pick(self, player_assignments):
        """Filters for available players and picks from internal order

        Args:
            player_assignments: dict of format
                   player : team that picked them

        Returns:
            String indicating chosen player
        """        
        #note that in the abstract class, no order is defined
        available_players = self.order[~self.order.index.isin(player_assignments.keys())]
        player = self.pick_from_order(available_players)
        return player
    
class ZAgent(SimpleAgent):
    """Agent which drafts using a Z-score based order

    The Z-score is calculated as the sum of normalized category attributes. Parameters for the normalization are 
    computed from the entire dataset of NBA players. If a category is punted, that category will not be included
    in the sum

    Attributes:
        players: A list of players already chosen by this agent
        positions: Eligible positions of each possible player. Agents need this info to make sure they draft eligible teams
        order: Sorted series of player -> score
      
    """
    def __init__(self
                 , player_averages
                 , positions
                 , punting_cats =[] #categories to completely ignore
                 ):
        """Calculates the Z score and initializes the agent

        Args:
            player_avaerages: Dataframe with weekly category averages by player
            positions: Series of player -> list of eligible positions
            punting_cats: list of categories to ignore

        Returns:
            None

        """        
        super(ZAgent, self).__init__(positions)
        player_averages_scaled = pd.DataFrame(StandardScaler().fit_transform(player_averages)
                                            , index = player_averages.index
                                            ,columns = player_averages.columns)
        player_averages_scaled['tov'] = - player_averages_scaled['tov']
                
        #ZR: Order does not need to be a Series, it should just be a list. Will need to reorg a bunch for that though
        self.order = player_averages_scaled.drop(columns = punting_cats).sum(axis = 1).sort_values(ascending = False)
    
class ZPlusAgent(SimpleAgent):
    
    """Agent which drafts using a Z-score order, adjusted to normalize based on strong players

    The Z-score is calculated as the sum of normalized category attributes. Unlike the standard Z-score, Z-plus only 
    considers strong players for its normalization parameters. Strong players are defined as the top N by standard 
    Z-score. If a category is punted, that category will not be included in the sum

    Attributes:
        players: A list of players already chosen by this agent
        positions: Series of player -> list of eligible positions. Agents need this info to make sure they draft eligible teams
        order: Sorted series of player -> score
      
    """
    def __init__(self
                 , player_averages
                 , positions
                 , punting_cats =[] 
                 ,n_players = 12*7*2 
                 ):
        """Calculates the Z-plus score and initializes the agent

        Args:
            player_averages: Dataframe with weekly category averages by player
            positions: Series of player -> list of eligible positions
            punting_cats: list of categories to ignore
            n_players: number of players to use for second-phase standardization

        Returns:
            None

        """
        super(ZPlusAgent, self).__init__(positions)

        first_order_scaled = pd.DataFrame(StandardScaler().fit_transform(player_averages)
                                            , index = player_averages.index
                                            ,columns = player_averages.columns)
        first_order_scaled['tov'] = - first_order_scaled['tov']
        
        first_order = first_order_scaled.drop(columns = punting_cats).sum(axis = 1).sort_values(ascending = False)
        top_players = first_order.index[0:n_players]
        
        plus_scaler = StandardScaler().fit(player_averages.loc[top_players])
        
        second_order_scaled = pd.DataFrame(plus_scaler.transform(player_averages)
                                            , index = player_averages.index
                                            ,columns = player_averages.columns)
        second_order_scaled['tov'] = - second_order_scaled['tov']
        
        self.order = second_order_scaled.drop(columns = punting_cats).sum(axis = 1).sort_values(ascending = False)
        
class GOAgent(SimpleAgent):
    
    """Agent which drafts using the Gaussian optimizer algorithm

    Roughly, the algorithm has two components
    - The Z-plus score, which is used primarily for early picks. Its weight decreases linearly for each successive pick
    - An estimate of winning probability based on hypothetical teams with each available player. The estimate is made
      with a Guassian approximation of point differential for each category, translated to winning probability via the
      normal CDF. Free throw percentage and field goal percentage are treated slightly different; they are assumed to 
      be binomials instead

    Attributes:
        players: A list of players already chosen by this agent
        positions: Series of player -> list of eligible positions. Agents need this info to make sure they draft eligible teams
        categories: list of categories that will be used for the actual season
        punting_cats: list of categories to ignore
        player_stats: dataframe with mean and variance stats for all categories for all players
        team_list: list of representative teams to optimize victory over
        
    """  
    
    def __init__(self
                 , season_df
                 , player_averages
                 , categories #ZR: Should fix the redundancy between this and punting_cats at some point
                 , positions
                 , winner_take_all = True
                 , punting_cats= []
                 , beta = 0):
        """Calculates the data that will be needed for every pass of the Gaussian Optimizer algorithm and
        and initalizes the agent

        Args:
            season_df: dataframe with weekly data for the season
            player_averages: Dataframe with weekly category averages by player
            positions: Series of player -> list of eligible positions
            winner_take_all: Boolean of whether to optimize for the winner-take-all format
                             If False, optimizes for total categories
            punting_cats: list of categories to ignore
            beta: weight factor for the Z-plus score
        Returns:
            None

        """
        super(GOAgent, self).__init__(positions)

        self.categories = categories
        self.punting_cats = punting_cats
        self.winner_take_all = winner_take_all
        
        #make a table with player averages + standard deviations as additional columns 
        player_stats = season_df.groupby(level = 'player').agg(['mean','var'])
        
        #it is helpful to keep track of the variance contribution of fg_pct and ft_pct
        fg = player_stats.loc[:, ('fg','mean')]
        fga = player_stats.loc[:, ('fga','mean')]
        player_stats.loc[:,'fg_var'] = fg/fga *(fga - fg) #derivation in notebook documentation
        
        ft = player_stats.loc[:, ('ft','mean')]
        fta = player_stats.loc[:, ('fta','mean')]
        player_stats.loc[:,'ft_var'] = ft/fta *(fta - ft)  
        
        self.player_stats = player_stats
        #since we want to beat teams that use simple z-scores, we'll use them as representative opponents
        representative_teams = run_draft([ZAgent(player_averages = player_averages,positions = positions) for x in range(12)] ,7)
        
        self.team_list = [[] for i in range(12)]
        for k,v, in representative_teams.items():
            self.team_list[v].append(k) 
                
        #for our own z_score estimates we want the best possible values, so we use z_plus
        self.z_scores = ZPlusAgent(player_averages = player_averages
                                   ,positions = positions
                                   ,punting_cats = punting_cats).order * beta
                                
    def make_pick(self, player_assignments):
        """Picks a player based on the Gaussian optimizer algorithm

        Args:
            player_assignments: dict of format
                   player : team that picked them
                   
        Returns:
            String indicating chosen player
        """
        round_n = len(self.players) 
        
        #1. Get the theoretical stats that your team will have, depending on which player you choose
        my_team_stats = self.player_stats.loc[self.players]
        available_players = self.player_stats.loc[~self.player_stats.index.isin(player_assignments.keys())]
        theoretical_stats = available_players + my_team_stats.sum()
        theoretical_stats = process_stat_df(theoretical_stats, self.categories)
        
        #grab the representative teams that were saved earlier
        other_teams = [x[:round_n + 1] for x in self.team_list]
        other_team_stats = pd.DataFrame(
            {i : self.player_stats.loc[self.player_stats.index.isin(other_teams[i])].agg('sum') for i in range(12)}
                                        ).T
        other_team_stats = process_stat_df(other_team_stats, self.categories)
        
        #a cross join gives us a row for all of our players by each representative team
        full_stat_df = theoretical_stats.reset_index().merge(other_team_stats
                                                             , how = 'cross'
                                                             , suffixes = ['_my','_other'])

        
        #with all the statistical parameters incolved, we can get probabilities of winning each category
        my_stat_cols = [c + '_my' for c in self.categories]
        other_stat_cols = [c + '_other' for c in self.categories]

        my_means = full_stat_df.loc[:,(my_stat_cols,'mean')].values
        other_means = full_stat_df.loc[:,(other_stat_cols,'mean')].values

        my_vars = full_stat_df.loc[:,(my_stat_cols,'var')].values
        other_vars = full_stat_df.loc[:,(other_stat_cols,'var')].values
        
        with np.errstate(invalid='ignore', divide='ignore'):
            z = np.where((my_vars + other_vars) > 0 
                                         , (my_means - other_means)/(np.sqrt(2 * (my_vars + other_vars)))
                                         , 0)

        c = pd.DataFrame((1 + special.erf(z))/2, columns = self.categories)
        c[self.punting_cats] = 0

        if self.winner_take_all:
            
            #the combinatorial calculation function computes the Poisson binomial cdf efficiently
            c_comp = 1 - c
            full_stat_df.loc[:,'win_probability'] = combinatorial_calculation(c, c_comp, self.categories)
        else:
            full_stat_df.loc[:,'win_probability'] = c.mean(axis = 1) 

        
        #the best player will roughly have the highest EV of winning against the other players
        player_scores = full_stat_df.groupby('player')['win_probability'].sum()
        
        #adjust the Gaussian optimizer's score with the saved z-scores
        player_scores_adjusted = player_scores * (round_n)/13 + self.z_scores * (13-round_n)/13
        
        player = self.pick_from_order(player_scores_adjusted.sort_values(ascending = False))
        return player
      