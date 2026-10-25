import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_stdio_tool_has_no_parameters_or_write_capability():
    async def exercise():
        server = StdioServerParameters(command=sys.executable,
                                       args=[str(Path('mcp-server/server.py').resolve())])
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                tools = (await client.list_tools()).tools
                assert [tool.name for tool in tools] == ['rehearsal_stock_summary']
                assert tools[0].input_schema.get('properties', {}) == {}
                result = await client.call_tool('rehearsal_stock_summary', {})
                assert not result.is_error
                text = str(result.content)
                assert 'password' not in text and 'customer' not in text
                denied = await client.call_tool('delete_stock', {})
                assert denied.is_error
    asyncio.run(exercise())
