# 3rd-party imports
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# msppotluck imports
from mcppotluck.baseball_server import router as mlb_router

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
