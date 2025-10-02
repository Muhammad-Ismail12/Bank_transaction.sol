from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI

from .config import settings
from .tools import TOOLS, FUNCTION_MAP


SYSTEM_PROMPT = (
    "You are a helpful medical office assistant for a doctor's appointment website. "
    "Help users find doctors, check availability, and manage appointments. "
    "When needed, call the appropriate tools to take real actions. "
    "Always confirm the result back to the user in clear language."
)


class AppointmentAgent:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key)

    def run(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Start with a system prompt
        full_messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        first = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = first.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None) or []

        if tool_calls:
            # Execute tool calls sequentially, append outputs
            for tool_call in tool_calls:
                name = tool_call.function.name
                raw_args = tool_call.function.arguments
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except Exception:
                    args = {}

                fn = FUNCTION_MAP.get(name)
                if not fn:
                    tool_output = {"error": f"Unknown tool: {name}"}
                else:
                    try:
                        tool_output = fn(**args)
                    except Exception as exc:
                        tool_output = {"error": str(exc)}

                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_output),
                })

            # Finalize response after providing tool outputs
            followup = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
            )
            final_msg = followup.choices[0].message
            return {
                "content": final_msg.content,
                "tool_calls": [
                    {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
                    for tc in tool_calls
                ],
            }

        # No tool calls, direct answer
        return {"content": msg.content, "tool_calls": []}