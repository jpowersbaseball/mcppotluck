# Base Python imports
import logging
import argparse
import datetime
import sys
import os
import json

# 3rd-party imports
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import uvicorn

# msppotluck imports
from mcppotluck.logger_config import setup_logging, get_logger
setup_logging()
logger = get_logger()
from mcppotluck.baseball_server import router as mlb_router
from mcppotluck import helpers

helpers.initplayermap()

def main(): # type: () -> None
    leParser = argparse.ArgumentParser()
    leParser.add_argument('--operation', help='What do you want MCP Potluck to do? (test|mcp)')
    leParser.add_argument('--config', help='A JSON file with settings, credentials, etc.')
    lesArgs = leParser.parse_args()
  
    if not hasattr(lesArgs, 'operation') or lesArgs.operation is None:
        logger.error('The MCP needs to know what to do.')
        leParser.print_help()
        sys.exit(2)
  
    configs = {}
    if hasattr(lesArgs, 'config') and lesArgs.config is not None:
        with open(lesArgs.config, "r") as f:
            configs = json.load(f)
  
    if lesArgs.operation == 'test':
        logger.info("I think I am getting MLB standings for 2025")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_major_league_standings(2025), indent=2))
        logger.info("I think I am getting 2025 batting data for the Nationals")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_team_batting_data(120, 2025), indent=2))
        logger.info("I think I am getting 2025 pitching data for the Nationals")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_team_pitching_data(120, 2025), indent=2))
        logger.info("I think I am getting 2025 roster data for the Nationals")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_roster(120, 2025), indent=2))
        logger.info("I think I am getting 2025 batting data for Aaron Judge")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_player_batting_data(592450, 2025), indent=2))
        logger.info("I think I am getting 2025 pitching data for Allan Winans")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.get_player_pitching_data(642216, 2025), indent=2))
        logger.info("I think I am looking up Aaron Judge's player ID")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.lookup_player_id("Aaron Judge"), indent=2))
        logger.info("I think I am looking up the Washington Nationals team ID")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.lookup_team_id("Washington Nationals"), indent=2))
        logger.info("I think I am looking up the Nationals team ID")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.lookup_team_id("Nationals"), indent=2))
        logger.info("I think I am getting Aaron Judge's current team")
        logger.info("=============================================")
        logger.info(json.dumps(helpers.getTeamForPlayer(592450), indent=2))
        
    elif lesArgs.operation == 'mcp':
        # Initialize Fast API
        app = FastAPI(
            title="MLB API MCP Server",
            description="Model Context Protocol server providing MLB statistics and baseball data APIs",
            version="0.1.0"
        )

        # Initialize MCP server
        mcp = FastApiMCP(app,
            describe_all_responses=True,
            describe_full_response_schema=True
        )

        mcp.mount()

        app.include_router(mlb_router)

        mcp.setup_server()

        uvicorn.run(app, host="127.0.0.1", port=8080)

if __name__ == "__main__":
    main()
