import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run():
    params = StdioServerParameters(
        command="uvx",
        args=["--from", "biz-dfch-specmgr[mcp, similarity]", "specmgr", "mcp"],
        cwd=str(Path(sys.argv[1])),
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            for name in sys.argv[2:]:
                t = next(x for x in tools.tools if x.name == name)
                print(f"=== {name} ===")
                print(json.dumps(t.input_schema, indent=1))


asyncio.run(run())
