import json
from typing import List, Dict, Any, Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import MATIC_STUDIO_EMAIL_PROMPT, MATIC_STUDIO_EMAIL_EXAMPLES
from src.core.tools import Tool, MATIC_STUDIO_TOOLS


class EmailAgent(BaseAgent):
    def __init__(self, tools: List[Tool] = None, **kwargs):
        super().__init__(**kwargs)
        self.tools = tools or [tool for tool in MATIC_STUDIO_TOOLS if tool.name == "compose_inquiry_email"]
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.show_reasoning = True
        self.enable_memory = True
    
    def process(self, user_input: str) -> str:
        reasoning_trace = []
        messages = [{"role": "system", "content": MATIC_STUDIO_EMAIL_PROMPT}]
        
        # Add few-shot examples
        for example in MATIC_STUDIO_EMAIL_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # Call LLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to use tools
        if response_message.tool_calls:
            reasoning_trace.append("📧 **Composing professional inquiry email...**\n")
            
            # Execute tool calls
            tool_results = []
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                reasoning_trace.append(f"🔧 **Using {tool_name}** with client information")
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                    reasoning_trace.append(f"✅ **Email composed successfully**\n")
            
            # Add tool results to messages and get final response
            messages.append(response_message)
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": result["output"],
                    "tool_call_id": result["tool_call_id"]
                })
            
            reasoning_trace.append("💭 **Finalizing email with additional guidance...**\n\n---\n")
            
            # Get final response with tool results
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = response_message.content
        
        # Update conversation history if memory is enabled
        if self.enable_memory:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_content})
        
        if self.show_reasoning and reasoning_trace:
            return "\n".join(reasoning_trace) + "\n" + final_content
        return final_content
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [{"role": "system", "content": MATIC_STUDIO_EMAIL_PROMPT}]
        
        # Add few-shot examples
        for example in MATIC_STUDIO_EMAIL_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # For email composition, we'll use non-streaming to get complete email
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            yield "📧 **Composing professional inquiry email...**\n\n"
            
            # Execute tool calls
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                yield f"🔧 **Using {tool_name}** with client information\n"
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    yield "✅ **Email composed successfully**\n\n"
                    
                    # Add tool results to messages
                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
            
            yield "💭 **Finalizing email with additional guidance...**\n\n---\n\n"
            
            # Get final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = response_message.content
        
        # Stream the final content word by word
        words = final_content.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
        
        # Update conversation history
        if self.enable_memory:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_content})
    
    def clear_memory(self):
        self.conversation_history = [] 