from typing import Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import MATIC_STUDIO_BASE_PROMPT


class SimpleAgent(BaseAgent):
    def process(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": MATIC_STUDIO_BASE_PROMPT},
            {"role": "user", "content": user_input}
        ]
        return self._call_llm(messages)
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [
            {"role": "system", "content": MATIC_STUDIO_BASE_PROMPT},
            {"role": "user", "content": user_input}
        ]
        yield from self._call_llm_stream(messages)