# Model Context Protocol Server for MLB Data

This module implements an MCP Server that allows an LLM to ask for baseball
data from the publically available [MLB Stats API](https://github.com/MajorLeagueBaseball/google-cloud-mlb-hackathon/tree/main/datasets/mlb-statsapi-docs).
Rather than directly exposing MLB endpoints via MCP, the module downselects
certain frequently used calls and implements RESTful endpoints to them.
This decision is because the MLB datasource is overly complex and expressive
for basic purposes, and we wanted to limit confusion.  The module then wraps
this simpler RESTful API with the MCP Server via FastMCP.  Although this
approach has been [derided as an anti-pattern](https://leehanchung.github.io/blogs/2025/05/17/mcp-is-not-rest-api/), it is made very straightforward
by the FastAPI and FastMCP modules, and reflects the reality that the majority
of useful data in the wild does originate from RESTful, JSON-producing APIs.

## Table of contents

- Purpose
- Installation
- Configuration
- Endpoints


## Purpose

The actual purpose of this module was to learn how to build an MCP Server.
The real-world use case that inspired it was a desire to make an LLM
that was trained in 2023 on data collected in 2022 (such as Clause Haiku 3.5)
but successfully answer complex questions about the 2025 MLB season.  The client
is implemented in the [MLB Chat module](https://github.com/jpowersbaseball/mlbchat).


## Installation

For now, this module runs as a CLI tool, and requires no installation
beyond:

```bash
   
   pip install -r requirements.txt
   ```

To run, simply invoke as a python module:

```bash
   
   python -m mcppotluck
   ```


## Configuration

The module runs the server at localhost:8080.  This can be changed by modifying
the following line in __main__.py:

```python
   
   uvicorn.run(app, host="127.0.0.1", port=8080)
   ```


## Endpoints

The API exposes 8 endpoints via both standard GET requests with CGI-style
arguments, and via MCP requests using the SSE protocol.  As this was built
with FastAPI, full documentation of the endpoints is available at /docs when
running.


### /mlb/standings

Returns a list of MLB teams with wins, losses, runs scored and allowed, and
[Pythagorean Record](https://en.wikipedia.org/wiki/Pythagorean_expectation).
There is an optional season argument which defaults to the current year.

Example: http://localhost:8080/mlb/standings?season=2025


### /mlb/teambatting

Returns team batting statistics, including all the basic counting statistics
and ratios like batting average and OPS.  Requires an MLB team ID number as the
team_id parameter, and an optional season argument which defaults to the
current year.

Example: http://localhost:8080/mlb/teambatting?team_id=120&season=2025


### /mlb/teampitching

Returns team pitching statistics, including all the basic counting statistics
and ratios like ERA and WHIP.  Requires an MLB team ID number as the
team_id parameter, and an optional season argument which defaults to the
current year.

Example: http://localhost:8080/mlb/teampitching?team_id=120&season=2025


### /mlb/roster

Returns a team's 40-man roster with MLB player ID and age. Requires an MLB 
team ID number as the team_id parameter, and an optional season argument 
which defaults to the current year.

Example: http://localhost:8080/mlb/roster?team_id=120&season=2025


### /mlb/playerbatting

Returns player batting statistics, including all the basic counting statistics
and ratios like batting average and OPS.  Requires an MLB player ID number as the
player_id parameter, and an optional season argument which defaults to the
current year.

Example: http://localhost:8080/mlb/playerbatting?player_id=624585&season=2025


### /mlb/playerpitching

Returns player pitching statistics, including all the basic counting statistics
and ratios like ERA and WHIP.  Requires an MLB player ID number as the
player_id parameter, and an optional season argument which defaults to the
current year.

Example: http://localhost:8080/mlb/playerpitching?player_id=665795&season=2025


### /mlb/playerid

Returns a player's MLB ID number.  Requires a player name string which MLB
recognizes (unclear how well this works).

Example: http://localhost:8080/mlb/playerid?player_name=Aaron+Judge


### /mlb/teamid

Returns a team's MLB ID number.  Requires a team name string which MLB
recognizes (unclear how well this works).

Example: http://localhost:8080/mlb/teamid?team_name=Washington+Nationals

### /mlb/playerteam

Returns a player's current MLB team name and ID.  Requires a player ID 

Example: http://localhost:8080/mlb/playerteam?player_id=624585

### Current maintainers

- [Joshua Powers (jpowersbaseball)](https://github.com/jpowersbaseball/mcppotluck)
