import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run():
    params = StdioServerParameters(
        command="uvx",
        args=["--from", "biz-dfch-specmgr[mcp, similarity]", "specmgr", "mcp"],
        cwd="/tmp/opencode/feat128/smoke",
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            for name in sys.argv[1:]:
                t = next(x for x in tools.tools if x.name == name)
                print(f"=== {name} ===")
                print(t.description)
                print()


asyncio.run(run())
