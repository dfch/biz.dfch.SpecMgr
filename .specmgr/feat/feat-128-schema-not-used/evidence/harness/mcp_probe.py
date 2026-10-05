# Throwaway MCP client for feat-128 Phase 100 (Task 100.100/100.110 harness).
# Connects to the PUBLISHED specmgr MCP server (uvx) with a controlled CWD,
# so the server resolves its document base dirs relative to that CWD exactly
# like the agent sessions do.

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CMD = [
    "uvx",
    "--from",
    "biz-dfch-specmgr[mcp, similarity]",
    "specmgr",
    "mcp",
]


async def run(action: str, cwd: Path, argv: list[str]) -> None:
    server_params = StdioServerParameters(command=CMD[0], args=CMD[1:], cwd=str(cwd))
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if action == "list":
                tools = await session.list_tools()
                print("TOOLS:")
                for t in tools.tools:
                    print(f"  {t.name}")
                prompts = await session.list_prompts()
                print("PROMPTS:")
                for p in prompts.prompts:
                    args = ",".join(a.name for a in (p.arguments or []))
                    print(f"  {p.name}({args}) -- {p.title}")
                resources = await session.list_resources()
                print("RESOURCES:")
                for r in resources.resources:
                    print(f"  {r.uri}")
            elif action == "get_prompt":
                name = argv[0]
                arguments = json.loads(argv[1]) if len(argv) > 1 else {}
                result = await session.get_prompt(name, arguments)
                for message in result.messages:
                    content = message.content
                    text = getattr(content, "text", str(content))
                    print(text)
            elif action == "call_tool":
                name = argv[0]
                arguments = json.loads(argv[1]) if len(argv) > 1 else {}
                result = await session.call_tool(name, arguments)
                print(json.dumps(result.model_dump(), indent=1, default=str))
            elif action == "read_resource":
                uri = argv[0]
                result = await session.read_resource(uri)
                for content in result.contents:
                    text = getattr(content, "text", None)
                    print(text if text is not None else str(content))
            else:
                print(f"unknown action {action}", file=sys.stderr)
                sys.exit(2)


def main() -> int:
    action = sys.argv[1]
    cwd = Path(sys.argv[2])
    argv = sys.argv[3:]
    asyncio.run(run(action, cwd, argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
