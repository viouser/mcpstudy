from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from agent.debugger import AgentDebugger
from tools.tool_registry import load_langchain_native_tools
from mcp_client.mcp_loader import load_mcp_tools


class LocalChatAgent:
    def __init__(
        self,
        model_name: str,
        tools: list,
        debugger: AgentDebugger | None = None,
        temperature: float = 0,
    ):
        self.model_name = model_name
        self.tools = tools
        self.debugger = debugger or AgentDebugger(enabled=False)

        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
        )

        self.agent = create_react_agent(
            self.llm,
            self.tools,
        )

        self.debugger.log(
            "agent_initialized",
            {
                "model_name": model_name,
                "temperature": temperature,
                "tool_count": len(self.tools),
                "tools": [
                    {
                        "name": getattr(tool, "name", None),
                        "description": getattr(tool, "description", None),
                    }
                    for tool in self.tools
                ],
            },
            flag="log_tool_routing",
        )

    @classmethod
    async def create(
        cls,
        model_name: str,
        temperature: float = 0,
        use_native_tools: bool = True,
        use_mcp: bool = True,
        debugger: AgentDebugger | None = None,
    ):
        debugger = debugger or AgentDebugger(enabled=False)

        all_tools = []

        if use_native_tools:
            native_tools = load_langchain_native_tools()

            debugger.log(
                "native_tools_loaded",
                {
                    "tool_count": len(native_tools),
                    "tools": [
                        {
                            "name": getattr(tool, "name", None),
                            "description": getattr(tool, "description", None),
                        }
                        for tool in native_tools
                    ],
                },
                flag="log_tool_routing",
            )

            all_tools.extend(native_tools)

        if use_mcp:
            mcp_tools = await load_mcp_tools(
                debugger=debugger,
                config_path="config.yaml",
            )

            all_tools.extend(mcp_tools)

        debugger.log(
            "all_tools_ready",
            {
                "tool_count": len(all_tools),
                "tools": [
                    {
                        "name": getattr(tool, "name", None),
                        "description": getattr(tool, "description", None),
                    }
                    for tool in all_tools
                ],
            },
            flag="log_tool_routing",
        )

        return cls(
            model_name=model_name,
            temperature=temperature,
            tools=all_tools,
            debugger=debugger,
        )

    def chat(self, user_input: str) -> str:
        self.debugger.log(
            "chat_started",
            {
                "user_input": user_input,
            },
            flag="log_tool_routing",
        )

        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        self.debugger.log(
            "agent_invoke_request",
            {
                "messages": messages,
            },
            flag="log_llm_requests",
        )

        try:
            result = self.agent.invoke(
                {
                    "messages": messages,
                }
            )

            self.debugger.log(
                "agent_invoke_response",
                {
                    "result": result,
                },
                flag="log_llm_responses",
            )

            final_answer = result["messages"][-1].content

            self.debugger.log(
                "chat_completed",
                {
                    "final_answer": final_answer,
                },
                flag="log_llm_responses",
            )

            return final_answer

        except Exception as error:
            self.debugger.log(
                "agent_invoke_error",
                {
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
                flag="log_mcp_errors",
            )

            return (
                "I ran into an error while invoking the local agent. "
                f"Error: {type(error).__name__}: {error}"
            )