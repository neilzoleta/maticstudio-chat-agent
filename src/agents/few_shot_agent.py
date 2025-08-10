from typing import Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import MATIC_STUDIO_ENHANCED_PROMPT, MATIC_STUDIO_FEW_SHOT_EXAMPLES


class FewShotAgent(BaseAgent):
    def process(self, user_input: str) -> str:
        messages = [{"role": "system", "content": MATIC_STUDIO_ENHANCED_PROMPT}]
        
        # Add few-shot examples
        for example in MATIC_STUDIO_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return self._call_llm(messages)
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [{"role": "system", "content": MATIC_STUDIO_ENHANCED_PROMPT}]
        
        # Add few-shot examples
        for example in MATIC_STUDIO_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        yield from self._call_llm_stream(messages)