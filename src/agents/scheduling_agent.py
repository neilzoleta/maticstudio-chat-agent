import json
from typing import List, Dict, Any, Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import MATIC_STUDIO_SCHEDULING_PROMPT
from src.core.tools import Tool, MATIC_STUDIO_TOOLS


class SchedulingAgent(BaseAgent):
    def __init__(self, tools: List[Tool] = None, **kwargs):
        super().__init__(**kwargs)
        self.tools = tools or [tool for tool in MATIC_STUDIO_TOOLS if tool.name == "schedule_consultation_meeting"]
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.show_reasoning = True
        self.enable_memory = True
    
    def process(self, user_input: str) -> str:
        # Handle "Learn more about MATICStudio" specifically
        if user_input.lower().strip() in ["learn more about maticstudio", "learn more about matic studio", "tell me about maticstudio", "tell me about matic studio"]:
            return self._get_matic_studio_overview()
        
        reasoning_trace = []
        messages = [{"role": "system", "content": MATIC_STUDIO_SCHEDULING_PROMPT}]
        
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
            reasoning_trace.append("📅 **Scheduling consultation meeting...**\n")
            
            # Execute tool calls
            tool_results = []
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                reasoning_trace.append(f"🔧 **Using {tool_name}** to schedule meeting")
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                    reasoning_trace.append(f"✅ **Meeting scheduled successfully**\n")
            
            # Add tool results to messages and get final response
            messages.append(response_message)
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": result["output"],
                    "tool_call_id": result["tool_call_id"]
                })
            
            reasoning_trace.append("💭 **Finalizing meeting details...**\n\n---\n")
            
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
    
    def _get_matic_studio_overview(self) -> str:
        """Return a precise overview of MATIC Studio for the 'Learn more' prompt"""
        return """**About MATIC Studio**

MATIC Studio is a Filipino-led business process automation studio that makes automation accessible, practical, and impactful for businesses worldwide.

**What We Do:**
• **Business Process Automation** - Custom solutions that actually work
• **Microsoft Power Platform** - Low-code apps, workflows, and automations  
• **M365 & VBA** - Excel and Office automation with macro scripting
• **RPA Solutions** - End-to-end automation using UiPath and Automation Anywhere
• **Data Visualization & BI** - Transform data into insights with Power BI and Tableau
• **AI-Powered Automation** - Intelligent systems that learn and adapt

**Our Approach:**
1. **Discovery & Diagnostics** - We listen under the hood of your business
2. **Deep Process Mapping** - We map your operations bolt by bolt  
3. **Custom-Built Automation** - We engineer solutions that fit your exact needs
4. **Testing & Fine-Tuning** - We ensure smooth operation
5. **Deployment & Support** - We launch with full support

**Industries We Serve:**
Healthcare, Banking, Oil & Gas, Payments, BPOs, and more.

To schedule a call, I'll need:
• Your full name
• Company name  
• Preferred date & time
• Email address

What's your company name and when would you like to connect?"""
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [{"role": "system", "content": MATIC_STUDIO_SCHEDULING_PROMPT}]
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # For scheduling, we'll use non-streaming to get complete meeting details
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            yield "📅 **Scheduling consultation meeting...**\n\n"
            
            # Execute tool calls
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                yield f"🔧 **Using {tool_name}** to schedule meeting\n"
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    yield "✅ **Meeting scheduled successfully**\n\n"
                    
                    # Add tool results to messages
                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
            
            yield "💭 **Finalizing meeting details...**\n\n---\n\n"
            
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