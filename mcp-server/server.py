"""Stdio MCP tool: aggregate rehearsal counts only; no parameters, SQL or credentials."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp.server.mcpserver import MCPServer
from agent_capabilities.stock import stock_summary

server = MCPServer('dealer-desk-local-evidence', instructions='Read-only synthetic aggregate counts. No production access.')


@server.tool()
def rehearsal_stock_summary() -> dict:
    """Return aggregate stock counts from the fixed local synthetic rehearsal, without customer data."""
    return stock_summary()


if __name__ == '__main__':
    server.run(transport='stdio')
