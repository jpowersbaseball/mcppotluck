# Standard Python imports
from datetime import datetime
import json

# 3rd-party imports
import requests
from requests.exceptions import HTTPError

mlb_teams = {
    "141": "Toronto Blue Jays",
    "147": "New York Yankees",
    "111": "Boston Red Sox",
    "139": "Tampa Bay Rays",
    "110": "Baltimore Orioles",
    "116": "Detroit Tigers",
    "142": "Minnesota Twins",
    "118": "Kansas City Royals",
    "114": "Cleveland Guardians",
    "145": "Chicago White Sox",
    "117": "Houston Astros",
    "136": "Seattle Mariners",
    "140": "Texas Rangers",
    "108": "Los Angeles Angels",
    "133": "Athletics",
    "143": "Philadelphia Phillies",
    "121": "New York Mets",
    "146": "Miami Marlins",
    "144": "Atlanta Braves",
    "120": "Washington Nationals",
    "112": "Chicago Cubs",
    "158": "Milwaukee Brewers",
    "138": "St. Louis Cardinals",
    "113": "Cincinnati Reds",
    "134": "Pittsburgh Pirates",
    "119": "Los Angeles Dodgers",
    "137": "San Francisco Giants",
    "135": "San Diego Padres",
    "109": "Arizona Diamondbacks",
    "115": "Colorado Rockies"
}

player2team = {}

mlbstatsapipref = 'http://statsapi.mlb.com/api/v1/'

def get_mlb_stats(
    endpoint: str
):
    """
    Request JSON from an MLB statsapi endpoint, return the JSON
    
    Args:
        endpoint (str): The endpoint to request, assumed to include all parts of the URL
    
    Returns:
        dict: The results of parsing the JSON response
    """
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        # access JSON content
        jsonResponse = response.json()
        return jsonResponse

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def calculate_pythagorean_wins(
    runs_scored: int,
    runs_allowed: int,
    games_played: int,
    exponent: float = 1.83
):
    """
    Calculate Bill James' Pythagorean wins and losses.
    
    The Pythagorean expectation formula:
    Win% = (Runs Scored)^exponent / ((Runs Scored)^exponent + (Runs Allowed)^exponent)
    
    Args:
        runs_scored (int): Total runs scored by the team
        runs_allowed (int): Total runs allowed by the team
        games_played (int): Total games played
        exponent (Optional[float]): Pythagorean exponent (default 1.83)
    
    Returns:
        dict: Dictionary containing pythagorean wins, losses, new win percentage
    """
    
    if runs_scored <= 0 or runs_allowed <= 0 or games_played <= 0:
        return {
                'pythagorean_wins': 0,
                'pythagorean_losses': 0,
                'pythagorean_win_pct': 0.0
            }    
    
    # Calculate Pythagorean winning percentage
    rs_exp = runs_scored ** exponent
    ra_exp = runs_allowed ** exponent
    
    pythagorean_win_pct = rs_exp / (rs_exp + ra_exp)
    
    # Calculate expected wins and losses
    pythagorean_wins = round(pythagorean_win_pct * games_played)
    pythagorean_losses = games_played - pythagorean_wins
    
    return {
        'pythagorean_wins': pythagorean_wins,
        'pythagorean_losses': pythagorean_losses,
        'pythagorean_win_pct': pythagorean_win_pct
    }

def get_major_league_standings(
    season: int
):
    """
    Get MLB standings for a given season (year).

    Parameters:
        season int: The year for which to retrieve standings.

    Returns:
        dict: Standings for the Major Leagues in the specified season. Also includes the actual wins and losses, runs 
        scored and allowed, and the Pythagorean wins and losses calculated per Bill James. Each key is a team ID and the
        value is another dict with the team's statistics and full name.

    """
    
    global mlbstatsapipref
    
    try:
        
        team_data = {}

        for curleagueid in [103, 104]:
            subleague_url = mlbstatsapipref + 'standings?standingsType=regularSeason&leagueId=' + str(curleagueid) + '&season=' + str(season)
            subleague_standings = get_mlb_stats(subleague_url)

            for curdivdata in subleague_standings['records']:
                for curteamdata in curdivdata['teamRecords']:
                    team_dict = {}
                    team_dict['team_id'] = curteamdata['team']['id']
                    team_dict['team_name'] = curteamdata['team']['name']
                    team_dict['wins'] = curteamdata['leagueRecord']['wins']
                    team_dict['losses'] = curteamdata['leagueRecord']['losses']
                    team_dict['runs_scored'] = curteamdata['runsScored']
                    team_dict['runs_allowed'] = curteamdata['runsAllowed']
                    curpyth = calculate_pythagorean_wins(team_dict['runs_scored'], team_dict['runs_allowed'], team_dict['wins'] + team_dict['losses'])
                    team_dict['pythagorean_wins'] = curpyth['pythagorean_wins']
                    team_dict['pythagorean_losses'] = curpyth['pythagorean_losses']
                    team_data[team_dict['team_id']] = team_dict

        return team_data
        
    except Exception as e:
        raise Exception(str(e))

def init_batting_stats():
    """
    Create a dictionary of batting statistics with all values zero-ed out.

    Returns:
        dict: Zeroed-out batting statistics. Batting statistics include hits, doubles, triples, 
        home runs, walks, strikeouts, intentional walks, stolen bases, caught stealing, runs, 
        rbi, ground outs, air outs, hit by pitch, at bats, plate appearances, games, batting 
        average, on-base percentage, slugging percentage, ops, PA per HR, PA per BB and PA per K.
    
    """
    
    retstats = {}
    
    retstats['games'] = 0
    retstats['hits'] = 0
    retstats['doubles'] = 0
    retstats['triples'] = 0
    retstats['home_runs'] = 0
    retstats['walks'] = 0
    retstats['strikeouts'] = 0
    retstats['intentional_walks'] = 0
    retstats['stolen_bases'] = 0
    retstats['caught_stealing'] = 0
    retstats['runs'] = 0
    retstats['rbi'] = 0
    retstats['ground_outs'] = 0
    retstats['air_outs'] = 0
    retstats['hit_by_pitch'] = 0
    retstats['at_bats'] = 0
    retstats['plate_appearances'] = 0
    retstats['batting_average'] = 0
    retstats['on_base_percentage'] = 0.0
    retstats['slugging_percentage'] = 0.0
    retstats['ops'] = 0.0
    retstats['plate_appearances_per_home_run'] = 0.0
    retstats['plate_appearances_per_walk'] = 0.0
    retstats['plate_appearances_per_strikeout'] = 0.0
    
    return retstats

def get_team_batting_data(
    team_id: int,
    season: int
):
    """
    Get an MLB team's overall batting statistics

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season int: The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Batting statistics for the given team, along with basic identifying information.
        Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
        stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
        plate appearances, games, batting average, on-base percentage, slugging percentage, ops, PA per HR, PA per BB and PA per K.
    """
    
    global mlb_teams
    
    try:
        team_data = init_batting_stats()
        
        if str(team_id) not in mlb_teams:
            team_data['team_id'] = str(team_id)
            team_data['team_name'] = 'Unknown'
            return team_data
        
        team_stats_url = mlbstatsapipref + 'teams/' + str(team_id) + '/stats?group=hitting&stats=season&season=' + str(season)
        team_stats = get_mlb_stats(team_stats_url)
        team_split = team_stats['stats'][0]['splits'][0]
        team_data['team_id'] = str(team_id)
        team_data['team_name'] = team_split['team']['name']
        team_data['games'] = team_split['stat']['gamesPlayed']
        team_data['hits'] = team_split['stat']['hits']
        team_data['doubles'] = team_split['stat']['doubles']
        team_data['triples'] = team_split['stat']['triples']
        team_data['home_runs'] = team_split['stat']['homeRuns']
        team_data['walks'] = team_split['stat']['baseOnBalls']
        team_data['strikeouts'] = team_split['stat']['strikeOuts']
        team_data['intentional_walks'] = team_split['stat']['intentionalWalks']
        team_data['stolen_bases'] = team_split['stat']['stolenBases']
        team_data['caught_stealing'] = team_split['stat']['caughtStealing']
        team_data['runs'] = team_split['stat']['runs']
        team_data['rbi'] = team_split['stat']['rbi']
        team_data['ground_outs'] = team_split['stat']['groundOuts']
        team_data['air_outs'] = team_split['stat']['airOuts']
        team_data['hit_by_pitch'] = team_split['stat']['hitByPitch']
        team_data['at_bats'] = team_split['stat']['atBats']
        team_data['plate_appearances'] = team_split['stat']['plateAppearances']
        team_data['batting_average'] = float(team_split['stat']['avg'])
        team_data['on_base_percentage'] = float(team_split['stat']['obp'])
        team_data['slugging_percentage'] = float(team_split['stat']['slg'])
        team_data['ops'] = float(team_split['stat']['ops'])
        if int(team_data['plate_appearances']) > 0:
            team_data['plate_appearances_per_home_run'] = round(int(team_data['plate_appearances']) / int(team_data['home_runs']), 1)
            team_data['plate_appearances_per_walk'] = round(int(team_data['plate_appearances']) / int(team_data['walks']), 1)
            team_data['plate_appearances_per_strikeout'] = round(int(team_data['plate_appearances']) / int(team_data['strikeouts']), 1)
        
        return team_data
    except Exception as e:
        raise Exception(str(e))

def init_pitching_stats():
    """
    Create a dictionary of pitching statistics with all values zero-ed out.

    Returns:
        dict: Zeroed-out pitching statistics. Pitching statistics include wins, 
        losses, saves, games, games started, innings pitched, hits, home runs,
        walks, strikeouts, intentional walks, runs, earned runs, ground outs, 
        air outs, hit by pitch, batters faced, blown saves, batting average 
        against, on-base percentage against, slugging percentage against, 
        ops against, whip, era, strike percentage, strikeout to walk ratio,
        strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,
        home runs per 9 innings
    
    """
    
    retstats = {}
    
    retstats['wins'] = 0
    retstats['losses'] = 0
    retstats['saves'] = 0
    retstats['games'] = 0
    retstats['games_started'] = 0
    retstats['innings_pitched'] = 0.0
    retstats['hits'] = 0
    retstats['home_runs'] = 0
    retstats['walks'] = 0
    retstats['strikeouts'] = 0
    retstats['intentional_walks'] = 0
    retstats['runs'] = 0
    retstats['earned_runs'] = 0
    retstats['ground_outs'] = 0
    retstats['air_outs'] = 0
    retstats['hit_by_pitch'] = 0
    retstats['batters_faced'] = 0
    retstats['blown_saves'] = 0
    retstats['batting_average'] = 0.0
    retstats['on_base_percentage'] = 0.0
    retstats['slugging_percentage'] = 0.0
    retstats['ops'] = 0.0
    retstats['whip'] = 0.0
    retstats['era'] = 0.0
    retstats['strike_percentage'] = 0.0
    retstats['strikeout_walk_ratio'] = 0.0
    retstats['strikeout_per_9_inning'] = 0.0
    retstats['walks_per_9_inning'] = 0.0
    retstats['hits_per_9_inning'] = 0.0
    retstats['home_runs_per_9_inning'] = 0.0
    
    return retstats

def get_team_pitching_data(
    team_id: int,
    season: int
):
    """
    Get an MLB team's overall pitching statistics

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season int: The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Pitching statistics for the given team, along with basic identifying information.
        Pitching statistics include wins, 
        losses, saves, games, games started, innings pitched, hits, home runs,
        walks, strikeouts, intentional walks, runs, earned runs, ground outs, 
        air outs, hit by pitch, batters faced, blown saves, batting average 
        against, on-base percentage against, slugging percentage against, 
        ops against, whip, era, strike percentage, strikeout to walk ratio,
        strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,
        home runs per 9 innings
    """
    
    global mlb_teams
    
    try:
        team_data = init_pitching_stats()
        
        if str(team_id) not in mlb_teams:
            team_data['team_id'] = str(team_id)
            team_data['team_name'] = 'Unknown'
            return team_data
        
        team_stats_url = mlbstatsapipref + 'teams/' + str(team_id) + '/stats?group=pitching&stats=season&season=' + str(season)
        team_stats = get_mlb_stats(team_stats_url)
        team_split = team_stats['stats'][0]['splits'][0]
        team_data['team_id'] = team_id
        team_data['team_name'] = team_split['team']['name']
        team_data['wins'] = team_split['stat']['wins']
        team_data['losses'] = team_split['stat']['losses']
        team_data['saves'] = team_split['stat']['saves']
        team_data['games'] = team_split['stat']['gamesPlayed']
        team_data['games_started'] = team_split['stat']['gamesStarted']
        team_data['innings_pitched'] = float(team_split['stat']['inningsPitched'])
        team_data['hits'] = team_split['stat']['hits']
        team_data['home_runs'] = team_split['stat']['homeRuns']
        team_data['walks'] = team_split['stat']['baseOnBalls']
        team_data['strikeouts'] = team_split['stat']['strikeOuts']
        team_data['intentional_walks'] = team_split['stat']['intentionalWalks']
        team_data['runs'] = team_split['stat']['runs']
        team_data['earned_runs'] = team_split['stat']['earnedRuns']
        team_data['ground_outs'] = team_split['stat']['groundOuts']
        team_data['air_outs'] = team_split['stat']['airOuts']
        team_data['hit_by_pitch'] = team_split['stat']['hitByPitch']
        team_data['batters_faced'] = team_split['stat']['battersFaced']
        team_data['blown_saves'] = team_split['stat']['blownSaves']
        team_data['batting_average'] = float(team_split['stat']['avg'])
        team_data['on_base_percentage'] = float(team_split['stat']['obp'])
        team_data['slugging_percentage'] = float(team_split['stat']['slg'])
        team_data['ops'] = float(team_split['stat']['ops'])
        team_data['whip'] = float(team_split['stat']['whip'])
        team_data['era'] = float(team_split['stat']['era'])
        team_data['strike_percentage'] = team_split['stat']['strikePercentage']
        team_data['strikeout_walk_ratio'] = team_split['stat']['strikeoutWalkRatio']
        team_data['strikeout_per_9_inning'] = team_split['stat']['strikeoutsPer9Inn']
        team_data['walks_per_9_inning'] = team_split['stat']['walksPer9Inn']
        team_data['hits_per_9_inning'] = team_split['stat']['hitsPer9Inn']
        team_data['home_runs_per_9_inning'] = team_split['stat']['homeRunsPer9']
        
        return team_data
    except Exception as e:
        raise Exception(str(e))

def get_roster(
    team_id: int,
    season: int
):
    """
    Get an MLB team's current 40-man roster

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season int: The year for which to retrieve the roster.

    Returns:
        dict: The players on this team's 40-man roster, including their names and MLB unique identifiers.  The key is their unique identifier,
        and the value is the dict that contains that player's data.
    """
    
    global mlb_teams
    
    try:

        roster_data = {}

        if str(team_id) not in mlb_teams:
            return roster_data

        roster_url = mlbstatsapipref + 'teams/' + str(team_id) + '/roster?rosterType=40Man&season=' + str(season)
        roster_info = get_mlb_stats(roster_url)
        for curplayer in roster_info['roster']:
            player_data = {}
            player_data['player_id'] = curplayer['person']['id']
            player_data['player_name'] = curplayer['person']['fullName']
            player_data['position'] = curplayer['position']['name']
            roster_data[player_data['player_id']] = player_data

        return roster_data
    except Exception as e:
        raise Exception(str(e))

def get_player_batting_data(
    player_id: int,
    season: int
):
    """
    Get an MLB player's overall season batting statistics

    Parameters:
        player_id (int): The identifier used for this player by MLB's stats API
        season (int): The year for which to retrieve statistics.

    Returns:
        dict: Batting statistics for the given player, along with basic identifying information.
        Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
        stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
        plate appearances, games, batting average, on-base percentage, slugging percentage, ops, PA per HR, PA per BB and PA per K.

    """
    
    try:
        player_data = init_batting_stats()

        player_stats_url = mlbstatsapipref + 'people/' + str(player_id) + '?hydrate=stats(group=[hitting],type=season,season=' + str(season) + ')'
        player_stats = get_mlb_stats(player_stats_url)
        player_data['player_id'] = player_id
        player_data['player_name'] = player_stats['people'][0]['fullName']
        if str(player_id) in player2team:
            player_data['team_id'] = player2team[str(player_id)]['team_id']
            player_data['team_name'] = player2team[str(player_id)]['team_name']
        player_data['age'] = player_stats['people'][0]['currentAge']
        if 'stats' in player_stats['people'][0]:
            player_split = player_stats['people'][0]['stats'][0]['splits'][0]
            player_data['games'] = player_split['stat']['gamesPlayed']
            player_data['hits'] = player_split['stat']['hits']
            player_data['doubles'] = player_split['stat']['doubles']
            player_data['triples'] = player_split['stat']['triples']
            player_data['home_runs'] = player_split['stat']['homeRuns']
            player_data['walks'] = player_split['stat']['baseOnBalls']
            player_data['strikeouts'] = player_split['stat']['strikeOuts']
            player_data['intentional_walks'] = player_split['stat']['intentionalWalks']
            player_data['stolen_bases'] = player_split['stat']['stolenBases']
            player_data['caught_stealing'] = player_split['stat']['caughtStealing']
            player_data['runs'] = player_split['stat']['runs']
            player_data['rbi'] = player_split['stat']['rbi']
            player_data['ground_outs'] = player_split['stat']['groundOuts']
            player_data['air_outs'] = player_split['stat']['airOuts']
            player_data['hit_by_pitch'] = player_split['stat']['hitByPitch']
            player_data['at_bats'] = player_split['stat']['atBats']
            player_data['plate_appearances'] = player_split['stat']['plateAppearances']
            player_data['batting_average'] = float(player_split['stat']['avg'])
            player_data['on_base_percentage'] = float(player_split['stat']['obp'])
            player_data['slugging_percentage'] = float(player_split['stat']['slg'])
            player_data['ops'] = float(player_split['stat']['ops'])
            if int(player_data['plate_appearances']) > 0:
                player_data['plate_appearances_per_home_run'] = round(int(player_data['plate_appearances']) / int(player_data['home_runs']), 1)
                player_data['plate_appearances_per_walk'] = round(int(player_data['plate_appearances']) / int(player_data['walks']), 1)
                player_data['plate_appearances_per_strikeout'] = round(int(player_data['plate_appearances']) / int(player_data['strikeouts']), 1)
        
        return player_data
    except Exception as e:
        raise Exception(str(e))

def get_player_pitching_data(
    player_id: int,
    season: int
):
    """
    Get an MLB player's overall pitching statistics

    Parameters:
        player_id (int): The identifier used for this player by MLB's stats API
        season (int): The year for which to retrieve statistics.

    Returns:
        dict: Pitching statistics for the given player, along with basic identifying information.
        Pitching statistics include wins, losses, saves, games, games started, innings pitched, hits, home runs,
        walks, strikeouts, intentional walks, runs, earned runs, ground outs, air outs, hit by pitch, batters faced,
        blown saves, batting average against, on-base percentage against, slugging percentage against, ops against, whip,
        era, strike percentage, strikeout to walk ratio, strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,
        home runs per 9 innings

    Examples:
        - Get current pitching statistics for Allan Winans:
            /mlb/teampitching?player_id=642216
        - Get 2022 pitching statistics for Allan Winans:
            /mlb/teampitching?player_id=642216&season=2022
    """
    
    try:
        
        player_data = init_pitching_stats()
        
        player_stats_url = mlbstatsapipref + 'people/' + str(player_id) + '?hydrate=stats(group=[pitching],type=season,season=' + str(season) + ')'
        player_stats = get_mlb_stats(player_stats_url)
        player_data['player_id'] = player_id
        player_data['player_name'] = player_stats['people'][0]['fullName']
        if str(player_id) in player2team:
            player_data['team_id'] = player2team[str(player_id)]['team_id']
            player_data['team_name'] = player2team[str(player_id)]['team_name']
        player_data['age'] = player_stats['people'][0]['currentAge']
        if 'stats' in player_stats['people'][0]:
            player_split = player_stats['people'][0]['stats'][0]['splits'][0]
            player_data['wins'] = player_split['stat']['wins']
            player_data['losses'] = player_split['stat']['losses']
            player_data['saves'] = player_split['stat']['saves']
            player_data['games'] = player_split['stat']['gamesPlayed']
            player_data['games_started'] = player_split['stat']['gamesStarted']
            player_data['innings_pitched'] = float(player_split['stat']['inningsPitched'])
            player_data['hits'] = player_split['stat']['hits']
            player_data['home_runs'] = player_split['stat']['homeRuns']
            player_data['walks'] = player_split['stat']['baseOnBalls']
            player_data['strikeouts'] = player_split['stat']['strikeOuts']
            player_data['intentional_walks'] = player_split['stat']['intentionalWalks']
            player_data['runs'] = player_split['stat']['runs']
            player_data['earned_runs'] = player_split['stat']['earnedRuns']
            player_data['ground_outs'] = player_split['stat']['groundOuts']
            player_data['air_outs'] = player_split['stat']['airOuts']
            player_data['hit_by_pitch'] = player_split['stat']['hitByPitch']
            player_data['batters_faced'] = player_split['stat']['battersFaced']
            player_data['blown_saves'] = player_split['stat']['blownSaves']
            player_data['batting_average'] = float(player_split['stat']['avg'])
            player_data['on_base_percentage'] = float(player_split['stat']['obp'])
            player_data['slugging_percentage'] = float(player_split['stat']['slg'])
            player_data['ops'] = float(player_split['stat']['ops'])
            player_data['whip'] = float(player_split['stat']['whip'])
            player_data['era'] = float(player_split['stat']['era'])
            player_data['strike_percentage'] = float(player_split['stat']['strikePercentage'])
            player_data['strikeout_walk_ratio'] = float(player_split['stat']['strikeoutWalkRatio'])
            player_data['strikeout_per_9_inning'] = float(player_split['stat']['strikeoutsPer9Inn'])
            player_data['walks_per_9_inning'] = float(player_split['stat']['walksPer9Inn'])
            player_data['hits_per_9_inning'] = float(player_split['stat']['hitsPer9Inn'])
            player_data['home_runs_per_9_inning'] = float(player_split['stat']['homeRunsPer9'])
        
        return player_data
    except Exception as e:
        raise Exception(str(e))

def lookup_player_id(
    player_name: str
):
    """
    Looks up a player's ID using their name
    
    Args:
        player_name (str): the player's name
    
    Returns:
        dict: the player's ID and name, and if they are currently on 
        a 40-man roster, their team ID and name.
    """
    
    global player2team
    
    try:
        player_data = {}

        lookup_url = mlbstatsapipref + 'people/search?names=' + player_name
        lookup_data = get_mlb_stats(lookup_url)
        if 'people' in lookup_data and len(lookup_data['people']) > 0:
            player_data['player_name'] = lookup_data['people'][0]['fullName']
            player_data['player_id'] = lookup_data['people'][0]['id']
        else:
            player_data['player_name'] = 'NA'
            player_data['player_id'] = 0

        if str(player_data['player_id']) in player2team:
            player_data['team_id'] = player2team[str(player_data['player_id'])]['team_id']
            player_data['team_name'] = player2team[str(player_data['player_id'])]['team_name']

        return player_data
    except Exception as e:
        raise Exception(str(e))
    
def lookup_team_id(
    team_name: str
):
    """
    Gets the MLB unique identifier for a team given its full name. 

    Parameters:
        team_name str: The team's name

    Returns:
        dict: The team's name and MLB unique identifier

    """
    
    try:
        usename = team_name.lower().strip()
        
        name2id = {}
        name2beautiful = {}
        
        for curleagueid in [103, 104]:
            subleague_url = mlbstatsapipref + 'standings?standingsType=regularSeason&leagueId=' + str(curleagueid) + '&season=2025'
            subleague_standings = get_mlb_stats(subleague_url)
            for curdivdata in subleague_standings['records']:
                for curteamdata in curdivdata['teamRecords']:
                    cleanname = curteamdata['team']['name'].lower().strip()
                    name2id[cleanname] = curteamdata['team']['id']
                    name2beautiful[cleanname] = curteamdata['team']['name']
                    
        ret_data = {}
        if usename in name2id:
            ret_data['team_id'] = name2id[usename]
            ret_data['team_name'] = name2beautiful[usename]
        if len(ret_data) == 0:
            for curname, curid in name2id.items():
                if usename in curname:
                    ret_data['team_id'] = curid
                    ret_data['team_name'] = name2beautiful[curname]
        
        return ret_data
    except Exception as e:
        raise Exception(str(e))

def initplayermap():
    """
    Creates a mapping between player ids and their current teams.
    Stores locally in the helper variable player2team.
    
    """

    global mlb_teams, player2team
    
    curseason = datetime.now().year
    for curteamID, curteamName in mlb_teams.items():
        cur_roster = get_roster(int(curteamID), curseason)
        for cur_player_id, cur_player_data in cur_roster.items():
            cur_dict = {"team_id": curteamID, "team_name": curteamName, "player_name": cur_player_data["player_name"]}
            player2team[str(cur_player_id)] = cur_dict
    
def getTeamForPlayer(
    inPlayerID: int
):
    """
    Retrieves the current team for a player.

    Args:
        inPlayerID (int): The player's MLB ID
    
    Returns:
        dict: The team ID and name that the player is on,
              or "Unknown"
    """
    
    global player2team
    
    if str(inPlayerID) in player2team:
        return player2team[str(inPlayerID)]
    
    return {"team_id": "Unknown", "team_name": "Unknown", "player_name": "Unknown"}

    
