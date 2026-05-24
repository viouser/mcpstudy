import asyncio
import yaml
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.chat_agent import LocalChatAgent
from agent.debugger import AgentDebugger


def load_config(path: str = "config.yaml") -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, path)
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_debugger(config: dict) -> AgentDebugger:
    debug_config = config.get("debug", {})

    flags = {
        "log_llm_requests": debug_config.get("log_llm_requests", True),
        "log_llm_responses": debug_config.get("log_llm_responses", True),
        "log_tool_routing": debug_config.get("log_tool_routing", True),
        "log_tool_results": debug_config.get("log_tool_results", True),
        "log_mcp_startup": debug_config.get("log_mcp_startup", True),
        "log_mcp_tools": debug_config.get("log_mcp_tools", True),
        "log_mcp_errors": debug_config.get("log_mcp_errors", True),
    }

    return AgentDebugger(
        enabled=debug_config.get("enabled", False),
        log_to_file=debug_config.get("log_to_file", True),
        log_path=debug_config.get("log_path", "logs/agent_debug.log"),
        flags=flags,
    )


async def main():
    config = load_config()

    model_config = config.get("model", {})
    agent_config = config.get("agent", {})

    model_name = model_config.get("name", "llama3.1:8b")
    temperature = model_config.get("temperature", 0)

    use_native_tools = agent_config.get("use_native_tools", True)
    use_mcp = agent_config.get("use_mcp", True)

    debugger = build_debugger(config)

    debugger.log(
        "app_startup_config",
        {
            "model_name": model_name,
            "temperature": temperature,
            "use_native_tools": use_native_tools,
            "use_mcp": use_mcp,
        },
    )

    agent = await LocalChatAgent.create(
        model_name=model_name,
        temperature=temperature,
        use_native_tools=use_native_tools,
        use_mcp=use_mcp,
        debugger=debugger,
    )

    print("Local MCP-enabled agent started. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = agent.chat(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())