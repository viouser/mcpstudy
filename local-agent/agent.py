import os
import sys

# Add the parent directory to sys.path to find the 'agent' package
# and avoid shadowing the package name with this file
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from agent.chat_agent import LocalChatAgent
from agent.debugger import AgentDebugger

def load_config(path: str = "config.yaml") -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, path)
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    config = load_config()
    model_name = config["model"]["name"]

    # Setup debugger
    debug_config = config.get("debug", {})
    debugger = AgentDebugger(
        enabled=debug_config.get("enabled", False),
        log_to_file=debug_config.get("log_to_file", False),
        log_path=debug_config.get("log_path", "logs/agent_debug.log"),
    )

    agent = LocalChatAgent(
        model_name=model_name,
        debugger=debugger
    )

    print("Local agent started. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = agent.chat(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()