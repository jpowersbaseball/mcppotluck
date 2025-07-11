# 3rd-party imports
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException

# immo imports
from . import helpers

router = APIRouter(prefix="/mlb", tags=["MLB"])

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
        exponent (float): Pythagorean exponent (default 1.83)
    
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

@router.get(
    "/standings",
    operation_id="get_mlb_standings",
    description="""
Gets current MLB standings for a given season (year). If no season is provided or is facetious, defaults to the current year. 

Returns the standings for both the American League (AL) and National League (NL).

Includes the actual wins and losses, runs scored and allowed, and the Pythagorean wins and losses calculated per Bill James.

Optional parameters:
- `season`: The year for which standings will be returned.  Defaults to the current year.

Example:
- `/mlb/standings` (returns current season standings)
- `/mlb/standings?season=2022` (returns 2022 season standings)
"""
)
async def get_mlb_standings(
    season: Optional[int] = 2025
):
    """
    Get MLB standings for a given season (year).

    Parameters:
        season (Optional[int]): The year for which to retrieve standings. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Standings for the Major Leagues in the specified season. Also includes the actual wins and losses, runs 
        scored and allowed, and the Pythagorean wins and losses calculated per Bill James. Each key is a team ID and the
        value is another dict with the team's statistics and full name.

    Examples:
        - Get current season standings for both leagues:
            /mlb/standings
        - Get 2022 season standings:
            /mlb/standings?season=2022
    """
    
    try:
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        team_data = {}
        
        for curleagueid in [103, 104]:
            subleague_url = helpers.mlbstatsapipref + 'standings?standingsType=regularSeason&leagueId=' + str(curleagueid) + '&season=' + str(useseason)
            subleague_standings = helpers.get_mlb_stats(subleague_url)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teambatting",
    operation_id="get_team_batting",
    description="""
Gets an MLB team's batting statistics for a given season, or their current statistics if no season is given.
Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
plate appearances, games, batting average, on-base percentage, slugging percentage and ops.

Required parameters:
- `team_id`: The unique identifier number of the team.  

Optional parameters:
- `season`: The year for which statistics will be returned.  Defaults to the current year.

Example:
- `/mlb/teambatting?team_id=120` (returns current batting statistics for the Washington Nationals)
- `/mlb/teambatting?team_id=120&season=2022` (returns 2022 batting statistics for the Washington Nationals)
"""
)
async def get_team_batting(
    team_id: int,
    season: Optional[int] = 2025
):
    """
    Get an MLB team's overall batting statistics

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season (Optional[int]): The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Batting statistics for the given team, along with basic identifying information.
        Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
        stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
        plate appearances, games, batting average, on-base percentage, slugging percentage and ops.

    Examples:
        - Get current batting statistics for the Washington Nationals:
            /mlb/teambatting?team_id=120
        - Get 2022 batting statistics for the Washington Nationals:
            /mlb/teambatting?team_id=120&season=2022
    """
    
    try:
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        team_data = {}

        team_stats_url = helpers.mlbstatsapipref + 'teams/' + str(team_id) + '/stats?group=hitting&stats=season&season=' + str(useseason)
        team_stats = helpers.get_mlb_stats(team_stats_url)
        team_split = team_stats['stats'][0]['splits'][0]
        team_data['team_id'] = team_id
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
        
        return team_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teampitching",
    operation_id="get_team_pitching",
    description="""
Gets an MLB team's pitching statistics for a given season, or their current statistics if no season is given.
Pitching statistics include wins, losses, saves, games, games started, innings pitched, hits, home runs,
walks, strikeouts, intentional walks, runs, earned runs, ground outs, air outs, hit by pitch, batters faced,
blown saves, batting average against, on-base percentage against, slugging percentage against, ops against, whip,
era, strike percentage, strikeout to walk ratio, strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,

Required parameters:
- `team_id`: The unique identifier number of the team.  

Optional parameters:
- `season`: The year for which statistics will be returned.  Defaults to the current year.

Example:
- `/mlb/teampitching?team_id=120` (returns current pitching statistics for the Washington Nationals)
- `/mlb/teampitching?team_id=120&season=2022` (returns 2022 pitching statistics for the Washington Nationals)
"""
)
async def get_team_pitching(
    team_id: int,
    season: Optional[int] = 2025
):
    """
    Get an MLB team's overall pitching statistics

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season (Optional[int]): The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Pitching statistics for the given team, along with basic identifying information.
        Pitching statistics include wins, losses, saves, games, games started, innings pitched, hits, home runs,
        walks, strikeouts, intentional walks, runs, earned runs, ground outs, air outs, hit by pitch, batters faced,
        blown saves, batting average against, on-base percentage against, slugging percentage against, ops against, whip,
        era, strike percentage, strikeout to walk ratio, strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,
        home runs per 9 innings

    Examples:
        - Get current pitching statistics for the Washington Nationals:
            /mlb/teampitching?team_id=120
        - Get 2022 pitching statistics for the Washington Nationals:
            /mlb/teampitching?team_id=120&season=2022
    """
    
    try:
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        team_data = {}
        
        team_stats_url = helpers.mlbstatsapipref + 'teams/' + str(team_id) + '/stats?group=pitching&stats=season&season=' + str(useseason)
        team_stats = helpers.get_mlb_stats(team_stats_url)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/roster",
    operation_id="get_mlb_roster",
    description="""
Get the 40-man roster for a specific team by team_id and season

Returns the current roster for the specified team, including player IDs, names and positions.  
This is provided in a dictionary that maps the players' unique identifiers to their data.

Required parameters:
- `team_id`: The unique identifier number of the team.  

Optional parameters:
- `season`: The year for which the roster will be returned.  Defaults to the current year.

Examples:
- `/mlb/roster?team_id=147` (returns the New York Yankees 40-man roster)
- `/mlb/roster?team_id=147&season=2022` (returns the New York Yankees 40-man roster for 2022)
"""
)
async def get_mlb_roster(
    team_id: int,
    season: Optional[int] = 2025
):
    """
    Get the MLB 40-man roster for a given team for a given season.

    Parameters:
        team_id int: The identifier used for this team by MLB's stats API
        season (Optional[int]): The year for which to retrieve the roster. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: The players on this team's 40-man roster, including their names and MLB unique identifiers.  The key is their unique identifier,
        and the value is the dict that contains that player's data.

    Examples:
        - Get the current 40-man roster for the New York Yankees:
            /mlb/roster?team_id=147
        - Get the 2022 40-man roster for the New York Yankees:
            /mlb/roster?team_id=147&season=2022
    """
    try:
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        roster_data = {}
        
        roster_url = helpers.mlbstatsapipref + 'teams/' + str(team_id) + '/roster?rosterType=40Man&season=' + str(useseason)
        roster_info = helpers.get_mlb_stats(roster_url)
        for curplayer in roster_info['roster']:
            player_data = {}
            player_data['player_id'] = curplayer['person']['id']
            player_data['player_name'] = curplayer['person']['fullName']
            player_data['position'] = curplayer['position']['name']
            roster_data[player_data['player_id']] = player_data

        return roster_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/playerbatting",
    operation_id="get_player_batting",
    description="""
Gets an MLB player's batting statistics for a given season, or their current statistics if no season is given.
Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
plate appearances, games, batting average, on-base percentage, slugging percentage, age and ops.

Required parameters:
- `player_id`: The unique identifier number of the player.  

Optional parameters:
- `season`: The year for which statistics will be returned.  Defaults to the current year.

Example:
- `/mlb/playerbatting?player_id=592450` (returns current batting statistics for Aaron Judge)
- `/mlb/playerbatting?player_id=592450&season=2022` (returns 2022 batting statistics for Aaron Judge)
"""
)
async def get_player_batting(
    player_id: int,
    season: Optional[int] = 2025
):
    """
    Get an MLB player's overall season batting statistics

    Parameters:
        player_id int: The identifier used for this player by MLB's stats API
        season (Optional[int]): The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

    Returns:
        dict: Batting statistics for the given player, along with basic identifying information.
        Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
        stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
        plate appearances, games, batting average, on-base percentage, slugging percentage, age and ops.

    Examples:
        - Get current batting statistics for Aaron Judge:
            /mlb/teambatting?team_id=592450
        - Get 2022 batting statistics for Aaron Judge:
            /mlb/teambatting?team_id=592450&season=2022
    """
    
    try:
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        player_data = {}

        player_stats_url = helpers.mlbstatsapipref + 'people/' + str(player_id) + '?hydrate=stats(group=[hitting],type=season,season=' + str(useseason) + ')'
        player_stats = helpers.get_mlb_stats(player_stats_url)
        player_data['player_id'] = player_id
        player_data['player_name'] = player_stats['people'][0]['fullName']
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
        else:
            player_data['games'] = 0
            player_data['hits'] = 0
            player_data['doubles'] = 0
            player_data['triples'] = 0
            player_data['home_runs'] = 0
            player_data['walks'] = 0
            player_data['strikeouts'] = 0
            player_data['intentional_walks'] = 0
            player_data['stolen_bases'] = 0
            player_data['caught_stealing'] = 0
            player_data['runs'] = 0
            player_data['rbi'] = 0
            player_data['ground_outs'] = 0
            player_data['air_outs'] = 0
            player_data['hit_by_pitch'] = 0
            player_data['at_bats'] = 0
            player_data['plate_appearances'] = 0
            player_data['batting_average'] = 0.0
            player_data['on_base_percentage'] = 0.0
            player_data['slugging_percentage'] = 0.0
            player_data['ops'] = 0.0
        
        return player_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/playerpitching",
    operation_id="get_player_pitching",
    description="""
Gets an MLB player's pitching statistics for a given season, or their current statistics if no season is given.
Pitching statistics include wins, losses, saves, games, games started, innings pitched, hits, home runs,
walks, strikeouts, intentional walks, runs, earned runs, ground outs, air outs, hit by pitch, batters faced,
blown saves, batting average against, on-base percentage against, slugging percentage against, ops against, whip,
era, strike percentage, strikeout to walk ratio, strikeouts per 9 innings, walks per 9 innings, hits per 9 innings,

Required parameters:
- `player_id`: The unique identifier number of the player.  

Optional parameters:
- `season`: The year for which statistics will be returned.  Defaults to the current year.

Example:
- `/mlb/playerpitching?player_id=642216` (returns current pitching statistics for Allan Winans)
- `/mlb/playerpitching?player_id=642216&season=2022` (returns 2022 pitching statistics for Allan Winans)
"""
)
async def get_player_pitching(
    player_id: int,
    season: Optional[int] = 2025
):
    """
    Get an MLB player's overall pitching statistics

    Parameters:
        player_id int: The identifier used for this player by MLB's stats API
        season (Optional[int]): The year for which to retrieve statistics. Defaults to the current year if not provided or if the value is facetious.

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
        useseason = datetime.now().year
        if season is not None and season < useseason and season > 1876:
            useseason = season
        
        player_data = {}
        
        player_stats_url = helpers.mlbstatsapipref + 'people/' + str(player_id) + '?hydrate=stats(group=[pitching],type=season,season=' + str(useseason) + ')'
        player_stats = helpers.get_mlb_stats(player_stats_url)
        player_data['player_id'] = player_id
        player_data['player_name'] = player_stats['people'][0]['fullName']
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
        else:
            player_data['wins'] = 0
            player_data['losses'] = 0
            player_data['saves'] = 0
            player_data['games'] = 0
            player_data['games_started'] = 0
            player_data['innings_pitched'] = 0.0
            player_data['hits'] = 0
            player_data['home_runs'] = 0
            player_data['walks'] = 0
            player_data['strikeouts'] = 0
            player_data['intentional_walks'] = 0
            player_data['runs'] = 0
            player_data['earned_runs'] = 0
            player_data['ground_outs'] = 0
            player_data['air_outs'] = 0
            player_data['hit_by_pitch'] = 0
            player_data['batters_faced'] = 0
            player_data['blown_saves'] = 0
            player_data['batting_average'] = 0.0
            player_data['on_base_percentage'] = 0.0
            player_data['slugging_percentage'] = 0.0
            player_data['ops'] = 0.0
            player_data['whip'] = 0.0
            player_data['era'] = 0.0
            player_data['strike_percentage'] = 0.0
            player_data['strikeout_walk_ratio'] = 0.0
            player_data['strikeout_per_9_inning'] = 0.0
            player_data['walks_per_9_inning'] = 0.0
            player_data['hits_per_9_inning'] = 0.0
            player_data['home_runs_per_9_inning'] = 0.0
        
        return player_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/playerid",
    operation_id="lookup_player",
    description="""
Gets the MLB unique identifier for a player given his full name. 

Returns the player name and identifier given the name as input.

Required parameters:
- `player_name`: The full text name of the player, for example "Aaron Judge"

Example:
- `/mlb/playerid?player_name=Aaron+Judge` (returns MLB unique identifier 592450)
"""
)
async def lookup_player(
    player_name: str
):
    """
    Gets the MLB unique identifier for a player given his full name. 

    Parameters:
        player_name str: The player's name

    Returns:
        dict: The player's name and MLB unique identifier

    Examples:
        - Get Aaron Judge's MLB unique id:
            /mlb/player_name=Aaron+Judge
    """
    
    try:
        player_data = {}
        
        lookup_url = helpers.mlbstatsapipref + 'people/search?names=' + player_name
        lookup_data = helpers.get_mlb_stats(lookup_url)
        if 'people' in lookup_data and len(lookup_data['people']) > 0:
            player_data['player_name'] = lookup_data['people'][0]['fullName']
            player_data['player_id'] = lookup_data['people'][0]['id']
        else:
            player_data['player_name'] = 'NA'
            player_data['player_id'] = 0
        
        return player_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teamid",
    operation_id="lookup_team",
    description="""
Gets the MLB unique identifier for a team given its full name. 

Returns the team name and identifier given the name as input.

Required parameters:
- `team_name`: The full text name of the team, for example "New York Yankees"

Example:
- `/mlb/teamid?team_name=New+York+Yankees` (returns MLB unique identifier 149)
"""
)
async def lookup_team(
    team_name: str
):
    """
    Gets the MLB unique identifier for a team given its full name. 

    Parameters:
        team_name str: The team's name

    Returns:
        dict: The team's name and MLB unique identifier

    Examples:
        - Get the New+York+Yankees's MLB unique id:
            /mlb/team_name=New+York+Yankees
    """
    
    try:
        usename = team_name.lower().strip()
        
        name2id = {}
        name2beautiful = {}
        
        for curleagueid in [103, 104]:
            subleague_url = helpers.mlbstatsapipref + 'standings?standingsType=regularSeason&leagueId=' + str(curleagueid) + '&season=2025'
            subleague_standings = helpers.get_mlb_stats(subleague_url)
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
        raise HTTPException(status_code=500, detail=str(e))
