import json
import re
from typing import Optional, Dict, Any


class ToolRouter:
    def __init__(self, tools: dict):
        self.tools = tools

    def build_tool_selection_prompt(self, user_input: str) -> str:
        tool_descriptions = []

        for name, tool in self.tools.items():
            tool_descriptions.append(
                {
                    "name": name,
                    "description": tool.description,
                }
            )

        return f"""
You are a tool router.

Your job is to decide whether the user's request requires one of the available tools.

Available tools:
{json.dumps(tool_descriptions, indent=2)}

User request:
{user_input}

Return ONLY valid JSON.

If a tool is needed, return:
{{
  "use_tool": true,
  "tool": "tool_name",
  "arguments": {{
    "arg1": "value"
  }}
}}

If no tool is needed, return:
{{
  "use_tool": false
}}

Rules:
- Do not explain your answer.
- Do not wrap the JSON in markdown.
- Do not include comments.
- Use only tools from the available tools list.
"""

    def deterministic_route(self, user_input: str) -> Optional[Dict[str, Any]]:
        text = user_input.lower()

        if "memory" in text and "vm" in text:
            numbers = re.findall(r"\d+(?:\.\d+)?", text)

            if len(numbers) >= 2:
                vm_count = int(float(numbers[0]))
                memory_per_vm_gb = float(numbers[1])
                overhead_percent = 15

                if len(numbers) >= 3:
                    overhead_percent = float(numbers[2])

                return {
                    "tool": "estimate_vm_memory",
                    "arguments": {
                        "vm_count": vm_count,
                        "memory_per_vm_gb": memory_per_vm_gb,
                        "overhead_percent": overhead_percent,
                    },
                }

        return None

    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        json_text = match.group(0)

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None

    def parse_tool_decision(self, llm_response: str) -> Optional[Dict[str, Any]]:
        payload = self.extract_json(llm_response)

        if not payload:
            return None

        if payload.get("use_tool") is not True:
            return None

        tool_name = payload.get("tool")
        arguments = payload.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}"
            }

        if not isinstance(arguments, dict):
            return {
                "error": "Tool arguments must be a JSON object."
            }

        return {
            "tool": tool_name,
            "arguments": arguments,
        }

    def run_tool(self, tool_name: str, arguments: dict) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}"
            }

        try:
            result = self.tools[tool_name].run(**arguments)

            return {
                "tool": tool_name,
                "arguments": arguments,
                "result": result,
            }

        except Exception as error:
            return {
                "tool": tool_name,
                "arguments": arguments,
                "error": str(error),
            }