from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.debugger import AgentDebugger
from mcp_client.mcp_config import load_enabled_mcp_servers


async def load_mcp_tools(
    debugger: AgentDebugger | None = None,
    config_path: str = "config.yaml",
):
    debugger = debugger or AgentDebugger(enabled=False)

    mcp_servers = load_enabled_mcp_servers(config_path)

    debugger.log(
        "mcp_enabled_servers",
        {
            "server_count": len(mcp_servers),
            "servers": list(mcp_servers.keys()),
            "server_configs": mcp_servers,
        },
        flag="log_mcp_startup",
    )

    if not mcp_servers:
        debugger.log(
            "mcp_no_enabled_servers",
            "No enabled MCP servers found.",
            flag="log_mcp_startup",
        )
        return []

    try:
        client = MultiServerMCPClient(mcp_servers)

        debugger.log(
            "mcp_client_created",
            {
                "server_count": len(mcp_servers),
                "servers": list(mcp_servers.keys()),
            },
            flag="log_mcp_startup",
        )

        tools = await client.get_tools()

        debugger.log(
            "mcp_tools_loaded",
            {
                "tool_count": len(tools),
                "tools": [
                    {
                        "name": getattr(tool, "name", None),
                        "description": getattr(tool, "description", None),
                    }
                    for tool in tools
                ],
            },
            flag="log_mcp_tools",
        )

        return tools

    except Exception as error:
        debugger.log(
            "mcp_load_error",
            {
                "error_type": type(error).__name__,
                "error": str(error),
                "servers": list(mcp_servers.keys()),
            },
            flag="log_mcp_errors",
        )

        return []