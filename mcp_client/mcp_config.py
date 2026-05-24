import yaml
import os

def load_config(path: str = "config.yaml") -> dict:
    if not os.path.isabs(path) and not os.path.exists(path):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alt_path = os.path.join(parent_dir, "local-agent", path)
        if os.path.exists(alt_path):
            path = alt_path
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_enabled_mcp_servers(path: str = "config.yaml") -> dict:
    config = load_config(path)

    all_servers = config.get("mcp_servers", {})
    enabled_servers = {}

    for server_name, server_config in all_servers.items():
        if server_config.get("enabled", True):
            clean_config = dict(server_config)
            clean_config.pop("enabled", None)
            enabled_servers[server_name] = clean_config

    return enabled_servers