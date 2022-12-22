from src.helper_functions import round_robin_opponent
import numpy as np

def run_draft(agents
              , n_rounds):
    """Run a snake draft

    Snake drafts wrap around like 1 -> 2 -> 3 -> 3 -> 2 -> 1 -> 1 -> 2 -> 3 etc. 
    
    Args:
        agents: list of Agents, which are required to have make_pick() methods
        n_rounds: number of rounds to do of the snake draft. Each drafter will get n_rounds * 2 players
        
    Returns:
        dictionary of player assignments with the structure
         {'player name' : team_number } 
    """
    
    player_assignments = {}
    
    for i in range(n_rounds):
        for j in range(len(agents)):
            
            agent = agents[j]
            chosen_player = agent.make_pick(player_assignments)
            player_assignments[chosen_player] = j
            
        for j in reversed(range(len(agents))):
            agent = agents[j]
            chosen_player = agent.make_pick(player_assignments)
            player_assignments[chosen_player] = j

    return player_assignments

def run_multiple_seasons(teams
                         , season_df
                         , categories
                         , n_seasons = 100 
                         , n_weeks = 25
                         , winner_take_all = True):
    """Simulate multiple seasons with the same drafters 
    
    Weekly performances are sampled from a dataframe of real season performance
    Teams win weeks by winning more categories than their opponents. They win seasons by winning the
    most weeks of all players 
    
    Args:
        teams: player assignment dict, as produced by the run_draft() functoin
        season_df: dataframe of weekly numbers per players. These will be sampled to simulate seasons
        n_seasons: number of seasons to simulate
        n_weeks: number of weeks per season
        winner_take_all: If True, the winner of a majority of categories in a week gets a point.
                         If false, each player gets a point for each category won 
        
    Returns:
        Series of winning percentages with the structure
         team_number : winning_percent  
    """
    #create a version of the essential info dataframe which incorporate team information for this season
    season_df = season_df.reset_index().drop(columns = 'week')
    season_df.loc[:,'team'] = season_df['player'].map(teams) 
    season_df = season_df.dropna(subset = ['team'])

    #use sampling to simulate many seasons at the same time
    #assuming each season has 11 weeks, we need 11 * n total rows of data per player
    #ZR: Note that for now a "week" of data is just one game per player
    #in real basketball multiple games are played per week, so we need to adjust for that 
    performances = season_df.groupby('player').sample(n_weeks*n_seasons, replace = True)
    performances.loc[:,'week'] = performances.groupby('player').cumcount()
    performances.loc[:,'season'] = performances['week'] // n_weeks #integer division seperates weeks in groups 

    #total team performances are simply the sum of statistics for each player 
    team_performances = performances.groupby(['season','team','week']).sum()
    team_performances['fg_pct'] = (team_performances['fg']/team_performances['fga']).fillna(0)
    team_performances['ft_pct'] = (team_performances['ft']/team_performances['fta']).fillna(0)
    
    #for all categories except turnovers, higher numbers are better. So we invert turnovers 
    team_performances['tov'] = - team_performances['tov'] 
    
    team_performances = team_performances[categories] #only want category columns
    
    #we need to map each team to its opponent for the week. We do that with a formula for round robin pairing
    opposing_team_schedule = [(s,round_robin_opponent(t,w),w) for s, t, w in team_performances.index]
    opposing_team_performances = team_performances.loc[opposing_team_schedule]

    cat_wins = np.greater(team_performances.values,opposing_team_performances.values).sum(axis = 1)
    cat_ties = np.equal(team_performances.values,opposing_team_performances.values).sum(axis = 1)
    
    if winner_take_all:
        team_performances.loc[:,'tie'] = cat_wins + cat_ties/2 == len(categories)/2
        team_performances.loc[:,'win'] = cat_wins + cat_ties/2 > len(categories)/2
    else:
        team_performances.loc[:,'tie'] = cat_ties
        team_performances.loc[:,'win'] = cat_wins
        
    team_results = team_performances.groupby(['team','season']).agg({'win' : sum, 'tie' : sum})

    #a team cannot win the season if it has fewer wins than any other team 
    most_wins = team_results.groupby('season')['win'].transform('max')
    winners = team_results[team_results['win'] == most_wins]

    #among the teams with the most wins, ties are a tiebreaker 
    most_ties = winners.groupby('season')['tie'].transform('max')
    winners_after_ties = winners[winners['tie'] == most_ties]
    
    #assuming that payouts are divided when multiple teams are exactly tied, we give fractional points 
    winners_after_ties.loc[:,'winner_points'] = 1
    season_counts = winners_after_ties.groupby('season')['winner_points'].transform('count')
    winners_after_ties.loc[:,'winner_points_adjusted'] = 1/season_counts
    
    return winners_after_ties.groupby('team')['winner_points_adjusted'].sum()
    

    
   