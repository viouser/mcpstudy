import json
from datetime import datetime
from pathlib import Path
from typing import Any


class AgentDebugger:
    def __init__(
        self,
        enabled: bool = False,
        log_to_file: bool = True,
        log_path: str = "logs/agent_debug.log",
        flags: dict | None = None,
    ):
        self.enabled = enabled
        self.log_to_file = log_to_file
        self.log_path = Path(log_path)
        self.flags = flags or {}

        if self.log_to_file:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def is_enabled(self, flag: str | None = None) -> bool:
        if not self.enabled:
            return False

        if flag is None:
            return True

        return self.flags.get(flag, True)

    def log(self, label: str, data: Any = None,  flag: str | None = None):
        if not self.is_enabled(flag):
            return

        timestamp = datetime.now().isoformat(timespec="seconds")

        message = {
            "timestamp": timestamp,
            "label": label,
            "data": data,
        }

        pretty_message = self._format(message)

        print(f"\n[DEBUG] {label}")
        print(pretty_message)

        if self.log_to_file:
            with self.log_path.open("a", encoding="utf-8") as file:
                file.write(pretty_message)
                file.write("\n\n")

    def _format(self, value: Any) -> str:
        try:
            return json.dumps(value, indent=2, default=str)
        except TypeError:
            return str(value)