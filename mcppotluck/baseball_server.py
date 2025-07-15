# 3rd-party imports
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException

# mcppotluck imports
from . import helpers
from mcppotluck.logger_config import get_logger
logger = get_logger()

router = APIRouter(prefix="/mlb", tags=["MLB"])

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
        
        team_data = helpers.get_major_league_standings(useseason)
        
        return team_data
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teambatting",
    operation_id="get_team_batting",
    description="""
Gets an MLB team's batting statistics for a given season, or their current statistics if no season is given.
Batting statistics include hits, doubles, triples, home runs, walks, strikeouts, intentional walks,
stolen bases, caught stealing, runs, rbi, ground outs, air outs, hit by pitch, at bats,
plate appearances, games, batting average, on-base percentage, slugging percentage, ops, PA per HR,
PA per BB and PA per K.

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
        plate appearances, games, batting average, on-base percentage, slugging percentage, ops,
        PA per HR, PA per BB and PA per K.

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
        
        team_data = helpers.get_team_batting_data(team_id, useseason)

        return team_data
    except Exception as e:
        logger.error(str(e))
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
        
        team_data = helpers.get_team_pitching_data(team_id, useseason)
        
        return team_data
    except Exception as e:
        logger.error(str(e))
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
        
        roster_data = helpers.get_roster(team_id, useseason)
        
        return roster_data
    except Exception as e:
        logger.error(str(e))
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
        
        player_data = helpers.get_player_batting_data(player_id, useseason)
        
        return player_data
    except Exception as e:
        logger.error(str(e))
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
        
        player_data = helpers.get_player_pitching_data(player_id, useseason)
        
        return player_data
    except Exception as e:
        logger.error(str(e))
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
            /mlb/playerid?player_name=Aaron+Judge
    """
    
    try:
        player_data = helpers.lookup_player_id(player_name)
        
        return player_data
    except Exception as e:
        logger.error(str(e))
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
        ret_data = helpers.lookup_team_id(team_name)
        
        return ret_data
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/playerteam",
    operation_id="lookup_player_team",
    description="""
Gets the MLB unique identifier and name of the current team for a player given his id.

Returns the team id and name and the player's name given the player id as input.

Required parameters:
- `player_id`: The MLB id of the player, for example 592450

Example:
- `/mlb/playerteam?player_id=592450` (returns "New York Yankees", 147, "Aaron Judge")
"""
)
async def lookup_player_team(
    player_id: int
):
    """
    Gets the MLB unique identifier and name of the current team for a player given his id.

    Parameters:
        player_id (int): The MLB id of the player, for example 592450

    Returns:
        dict: The player's team's name and MLB unique identifier, and the player's name

    Examples:
        - Get Aaron Judge's current team:
            /mlb/playerteam?player_id=592450
    """
    
    try:
        player_data = helpers.getTeamForPlayer(player_id)
        
        return player_data
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

