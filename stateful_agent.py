import sys
import json
from typing import Dict, List, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Initialize our local tool-aware model
# Using llama3.1 to preserve the native function calling capabilities verified on Day 4
llm = ChatOllama(model="llama3.1", temperature=0.0)

# 2. Define our Multi-Tool Ecosystem
def check_service_health(service_name: str) -> str:
    """Checks overall service metrics."""
    services = {
        "checkout_service": {"status": "CRITICAL", "load": "94%"},
        "payment_service": {"status": "HEALTHY", "load": "22%"}
    }
    return json.dumps(services.get(service_name.lower().strip(), {"status": "UNKNOWN"}))

def fetch_live_container_logs(service_name: str) -> str:
    """Fetches real-time machine log data if a service is critical."""
    return f"LOG TRACE for {service_name}: [ERROR] OOMKilled - Memory limit reached in cgroup."

# Bind tools metadata directly to LangChain chat client
tools = [
    {
        "name": "check_service_health",
        "description": "Get current operational status and machine load metrics.",
        "parameters": {
            "type": "object",
            "properties": {"service_name": {"type": "string"}},
            "required": ["service_name"]
        }
    },
    {
        "name": "fetch_live_container_logs",
        "description": "Retrieve deep console engine error logs for a specific service.",
        "parameters": {
            "type": "object",
            "properties": {"service_name": {"type": "string"}},
            "required": ["service_name"]
        }
    }
]
llm_with_tools = llm.bind_tools(tools)

# 3. State Management Orchestrator
class SRETriageState:
    def __init__(self, user_query: str):
        self.messages: List[Any] = [
            SystemMessage(content="You are an advanced stateful SRE automation agent. Diagnose issues systemically using tools.")
        ]
        self.messages.append(HumanMessage(content=user_query))
        self.next_step: str = "llm_turn"

    def execute_turn(self):
        print(f"\n--- [State Loop] Executing: {self.next_step} ---")
        
        if self.next_step == "llm_turn":
            # Invoke model with current historical context array
            response = llm_with_tools.invoke(self.messages)
            self.messages.append(response)
            
            if response.tool_calls:
                self.next_step = "tool_turn"
            else:
                self.next_step = "end"
                
        elif self.next_step == "tool_turn":
            last_message = self.messages[-1]
            for tool_call in last_message.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                print(f"🛠️  Invoking bound tool: {t_name} with {t_args}")
                
                # Dynamic Tool routing execution
                if t_name == "check_service_health":
                    result = check_service_health(**t_args)
                elif t_name == "fetch_live_container_logs":
                    result = fetch_live_container_logs(**t_args)
                else:
                    result = "Error: Tool not found."
                
                print(f"📥 Tool Returned: {result}")
                # Append Tool result matched explicitly by ID to keep graph state healthy
                self.messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
            
            # Route back to model to see if it wants to execute a secondary tool or finish
            self.next_step = "llm_turn"

# 4. Pipeline Execution Run
if __name__ == "__main__":
    # Test a deep multi-step request
    query = "Check the health of checkout_service. If it's unstable, grab its live container logs to find the error."
    
    state = SRETriageState(query)
    
    # Run the state machine until it reaches a termination state
    max_loops = 5
    loop_count = 0
    while state.next_step != "end" and loop_count < max_loops:
        state.execute_turn()
        loop_count += 1
        
    print("\n================ FINAL SYSTEM DIAGNOSIS ================")
    print(state.messages[-1].content)
