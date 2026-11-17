#!/usr/bin/env python3
"""usage: X3D_MCP_DIR=path/to/x3d_mcp python validate_one.py FILE.x3d [...]  -- XSD + semantic validation through the x3d_mcp server (stdio)."""
import asyncio, json, re, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from pathlib import Path
def _find_repo():
    """X3D_MCP_DIR, else a sibling x3d_mcp checkout (../x3d_mcp, ../../x3d_mcp, ...) next to this repository."""
    if os.environ.get("X3D_MCP_DIR"):
        return os.environ["X3D_MCP_DIR"]
    for up in Path(__file__).resolve().parents[:5]:
        if (up / "x3d_mcp" / "src" / "server.py").is_file():
            return str(up / "x3d_mcp")
    sys.exit("validate_one: set X3D_MCP_DIR to an x3d_mcp checkout (and run with a Python that has its dependencies)")
REPO = _find_repo()
TXT = lambda r: "".join(getattr(c, "text", "") for c in r.content)
async def main(files):
    params = StdioServerParameters(command=sys.executable, args=["-m", "src.server"], cwd=REPO)
    async with stdio_client(params, errlog=open("/dev/null", "w")) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for fn in files:
                raw = open(fn, encoding="utf-8").read()
                v = json.loads(TXT(await s.call_tool("validate_x3d", {"content": raw, "encoding": "xml"})))
                t = TXT(await s.call_tool("validate_semantic", {"content": raw}))
                m = re.search(r"Found (\d+) error\(s\), (\d+) warning\(s\), (\d+) info", t)
                print(fn, "| XSD valid:", v.get("valid"), (v.get("errors") or [])[:3], "| semantic:", m.groups() if m else ("All Clear" if "All Clear" in t else t[:300]))
                if m and (int(m.group(1)) or int(m.group(2))): print(t[:1500])
if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
