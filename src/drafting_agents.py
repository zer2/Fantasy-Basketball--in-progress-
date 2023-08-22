"""Definitions of the drafting agent classes
Drafting agents choose players during drafts, according to pre-set algorithms 
"""

import pandas as pd
import numpy as np
from scipy import special
from src.simulation import run_draft
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm

from src.helper_functions import check_team_eligibility, combinatorial_calculation, calculate_coefficients, calculate_scores_from_coefficients

class SimpleAgent():
    """Abstract implementation of a simple agent, which picks players according to an internal order

    Cannot be used as an actual agent, because it has no order to pick from 

    Attributes:
        players: A list of players already chosen by this agent
        positions: Eligible positions of each possible player. Agents need this info to make sure they draft eligible teams
    """
    def __init__(self, positions, order = None):
        self.players = []
        self.positions = positions
        self.order = order
    
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
    
class HAgent(SimpleAgent):
    
    def __init__(self
                 , season_df
                 , positions
                 , n_players = 12*13 
                 , n_punts = 0
                 , winner_take_all = False

):
        """Calculates the rank order based on D-score

        Args:
            season_df: dataframe with weekly data for the season
            positions: Series of player -> list of eligible positions
            gamma: float, how much to scale the G-score
            epsilon: float, how much to weigh correlation
            n_players: number of players to use for second-phase standardization
            winner_take_all: Boolean of whether to optimize for the winner-take-all format
                             If False, optimizes for total categories
        Returns:
            None

        """
        super(HAgent, self).__init__(positions)
        
        self.winner_take_all = winner_take_all
        self.n_punts = n_punts
        
        all_players = pd.unique(season_df.index.get_level_values('player'))
        
        mean_of_means_1, var_of_means_1, mean_of_vars_1 = calculate_coefficients(season_df, all_players)
    
        first_order_scores = calculate_scores_from_coefficients(season_df
                                                       ,mean_of_means_1
                                                       ,var_of_means_1
                                                       ,mean_of_vars_1
                                                       ,alpha_weight = 1
                                                       ,beta_weight = 0)

        first_order_score_totals = first_order_scores.sum(axis = 1).sort_values(ascending = False)

        representative_player_set = first_order_score_totals.index[0:n_players]
        mean_of_means_2, var_of_means_2, mean_of_vars_2 = calculate_coefficients(season_df, representative_player_set)

        x_scores = calculate_scores_from_coefficients(season_df
                                                       ,mean_of_means_2
                                                       ,var_of_means_2
                                                       ,mean_of_vars_2
                                                       ,alpha_weight = 0
                                                       ,beta_weight = 1)

        x_scores.columns = ['pts','trb','ast','stl','blk','fg3','tov','ftp','fgp']

        x_scores = x_scores.loc[first_order_score_totals.sort_values(ascending = False).index]
        
        self.x_scores = x_scores
        self.score_table = x_scores.groupby([np.floor(x/12) for x in range(len(x_scores))]).agg(['mean','var'])
        
        
           
    def make_pick(self
                  , player_assignments):
        
        """Picks a player based on the D-score algorithm

        Args:
            player_assignments: dict of format
                   player : team that picked them
                   
        Returns:
            String indicating chosen player
        """
        round_n = len(self.players) 

        current_score_table = self.score_table[0:round_n].sum()

        x_self_sum = self.x_scores.loc[self.players].sum(axis = 0)

        diff_means =  x_self_sum - current_score_table.loc[(self.x_scores.columns,'mean')].droplevel(1)
        
        other_team_variance = self.score_table.loc[0:12,(self.x_scores.columns,'var')].sum().droplevel(1)
        rest_of_team_variance = self.score_table.loc[(round_n + 1):12,(self.x_scores.columns,'var')].sum().droplevel(1)

        diff_var = 26 + other_team_variance + rest_of_team_variance

        x_scores_available = self.x_scores[~self.x_scores.index.isin(player_assignments.keys())]

        win_probabilities = pd.DataFrame(norm.cdf(diff_means + x_scores_available, scale = np.sqrt(diff_var))
                                         ,index = x_scores_available.index)
        
        win_probabilities.columns = self.x_scores.columns

        #punt_rewards = - win_probabilities + np.array((self.v_scores * (12 - round_n))).reshape(1,9)
        #punt_rewards.loc[:,'no_punt'] = 0
        #optimal_punt_reward = punt_rewards.max(axis = 1)
      
        #punt
        win_probabilities = win_probabilities.where(win_probabilities.rank(axis=1, method='min', ascending=True) > self.n_punts, 0)


        if self.winner_take_all:
            adjusted_win_sums = combinatorial_calculation(win_probabilities
                                                          , 1 - win_probabilities
                                                          , categories = win_probabilities.columns
                             )
        else:
            adjusted_win_sums = win_probabilities.sum(axis = 1) #+ optimal_punt_reward
        
        players_sorted = adjusted_win_sums.sort_values(ascending = False)
        player = self.pick_from_order(players_sorted)
        return player
    
class PAgent():
    """Agent which takes a simple grid of scores and punts

    Cannot be used as an actual agent, because it has no order to pick from 

    Attributes:
        players: A list of players already chosen by this agent
        positions: Eligible positions of each possible player. Agents need this info to make sure they draft eligible teams
        scores: dataframe with column for category and row for player
    """
    def __init__(self, positions, scores, n_punts =0):
        self.players = []
        self.positions = positions
        self.scores = scores
        self.n_punts = n_punts
        
        self.running_score_sum = pd.Series([0] * len(scores.columns), index = scores.columns)
    
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
        available_players = self.scores[~self.scores.index.isin(player_assignments.keys())]
        theoretical_scores = available_players + self.running_score_sum
        
        punted_scores = theoretical_scores.where(theoretical_scores.rank(axis=1, method='min', ascending=True) > self.n_punts, 0)
        punted_sums = punted_scores.sum(axis = 1).sort_values(ascending = False)
            
        player = self.pick_from_order(punted_sums)
        self.running_score_sum = self.running_score_sum + available_players.loc[player]
        return player
    
