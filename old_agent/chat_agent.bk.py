from agent import debugger
import ollama

from agent.memory import ConversationMemory
from agent.prompts import SYSTEM_PROMPT
from tools.router import ToolRouter
from agent.debugger import AgentDebugger
from tools.tool_registry import load_native_tools


class LocalChatAgent:
    def __init__(
        self, 
        model_name: str,
        debugger: AgentDebugger | None = None,
    ):
        self.model_name = model_name
        self.memory = ConversationMemory()
        self.memory.initialize(SYSTEM_PROMPT)

        self.native_tools = load_native_tools()
        self.router = ToolRouter(self.native_tools)
        self.debugger = debugger

        self.debugger.log(
            "agent_initialized",
            {
                "model_name": self.model_name,
                "native_tools": list(self.native_tools.keys()),
            },
        )



    def ask_llm(self, messages):
        self.debugger.log(
            "llm_request",
            {
                "model": self.model_name,
                "messages": messages,
            },
        )
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
        )
        content = response["message"]["content"]
        self.debugger.log(
            "llm_response",
            {
                "content": content,
            },
        )

        return content

    def select_tool(self, user_input: str):
        self.debugger.log(
            "tool_selection_request",
            {
                "user_input": user_input,
            },
        )
        deterministic_decision = self.router.deterministic_route(user_input)

        self.debugger.log(
            "deterministic_route_result",
            deterministic_decision,
        )

        if deterministic_decision:
            return deterministic_decision
       
        tool_prompt = self.router.build_tool_selection_prompt(user_input)

        self.debugger.log(
            "tool_selection_prompt",
            {
                "tool_prompt": tool_prompt,
            },
        )

        messages = [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Return only valid JSON.",
            },
            {
                "role": "user",
                "content": tool_prompt,
            },
        ]

        llm_response = self.ask_llm(messages)

        tool_decision = self.router.parse_tool_decision(llm_response)

        self.debugger.log(
            "parsed_tool_decision",
            tool_decision,
        )

        return tool_decision

    def chat(self, user_input: str) -> str:
        self.debugger.log(
            "chat_request",
            {
                "user_input": user_input,
            },
        )

        tool_decision = self.select_tool(user_input)
        self.debugger.log(
            "tool_decision",
            tool_decision,
        )

        if tool_decision and "error" not in tool_decision:
            tool_name = tool_decision["tool"]
            arguments = tool_decision["arguments"]

            tool_result = self.router.run_tool(
                tool_name=tool_name,
                arguments=arguments,
            )
            self.debugger.log(
                "tool_result",
                tool_result,
            )

            final_messages = self.memory.get_messages() + [
                {
                    "role": "user",
                    "content": user_input,
                },
                {
                    "role": "tool",
                    "content": str(tool_result),
                },
                {
                    "role": "user",
                    "content": (
                        "Use the tool result above to answer my original question. "
                        "Mention internal routing "
                    ),
                },
            ]

            final_answer = self.ask_llm(final_messages)

            self.memory.add_user_message(user_input)
            self.memory.add_assistant_message(final_answer)

            self.debugger.log(
                "final_answer",
                final_answer,
            )

            return final_answer

        self.memory.add_user_message(user_input)

        final_answer = self.ask_llm(
            self.memory.get_messages()
        )

        self.memory.add_assistant_message(final_answer)

        self.debugger.log(
            "final_answer_no_tool",
            {
                "final_answer": final_answer,
            },
        )

        return final_answer