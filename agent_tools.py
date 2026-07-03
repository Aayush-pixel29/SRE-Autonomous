import sys
import json
import openai

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize our local Docker-hosted Ollama engine
client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL_NAME = "llama3.1"

# --- Define Mock System Operational Tools ---
def get_error_frequency(service_name: str) -> str:
    """Simulates querying a live Prometheus/Log database for specific service error metrics."""
    metrics = {
        "checkout_service": {"error_count": 42, "status": "CRITICAL", "last_incident": "2 mins ago"},
        "payment_service": {"error_count": 12, "status": "WARNING", "last_incident": "15 mins ago"},
        "inventory_service": {"error_count": 0, "status": "HEALTHY", "last_incident": "None"}
    }
    service = service_name.lower().strip()
    if service in metrics:
        return json.dumps({"service": service, **metrics[service]})
    return json.dumps({"error": f"Service '{service_name}' not tracked in operational telemetry."})

# Map string names to actual Python functions
AVAILABLE_TOOLS = {
    "get_error_frequency": get_error_frequency
}

# --- Define the JSON Schema for the LLM ---
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_error_frequency",
            "description": "Fetch real-time error frequency metrics and health status for a specific backend service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the target service (e.g., 'checkout_service', 'payment_service')."
                    }
                },
                "required": ["service_name"]
            }
        }
    }
]

def run_agent_turn(user_prompt: str):
    print(f"\n[Agent] User Request: '{user_prompt}'")
    
    system_instruction = (
        "You are an autonomous SRE triage agent. You have access to real-time system monitoring tools.\n"
        "If the user asks about system health or error counts, you MUST use the appropriate tool before answering.\n"
        "If no tool is required, answer normally based on your baseline context."
    )
    
    # Step 1: Ask the LLM if it wants to use a tool based on the schema
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        tools=tools_schema,
        tool_choice="auto",
        temperature=0.0
    )
    
    message = response.choices[0].message
    
    # Step 2: Check if the model decided to execute a function call
    if message.tool_calls:
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🧩 [Agent Decision] LLM triggered tool: '{function_name}' with args: {function_args}")
            
            # Execute the internal python function
            if function_name in AVAILABLE_TOOLS:
                tool_output = AVAILABLE_TOOLS[function_name](**function_args)
                print(f"📡 [Tool Execution Output] Result from system: {tool_output}")
                
                # Step 3: Provide the real tool feedback back to the LLM to get a final evaluation
                final_response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt},
                        message, # Pass the model's original tool call intent back
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": tool_output
                        }
                    ]
                )
                return final_response.choices[0].message.content
    else:
        print("✍️ [Agent Decision] No tool execution needed. Processing direct response.")
        return message.content

if __name__ == "__main__":
    # Test Scenario 1: Forcing a Tool Call
    print("--- Starting Agent Scenario 1 ---")
    output_1 = run_agent_turn("Can you pull the current error rates for the checkout_service right now?")
    print(f"\n[Final Agent Answer]:\n{output_1}")
    
    print("\n" + "="*60 + "\n")
    
    # Test Scenario 2: Standard response without needing tools
    print("--- Starting Agent Scenario 2 ---")
    output_2 = run_agent_turn("Explain what an SRE does in a software startup.")
    print(f"\n[Final Agent Answer]:\n{output_2}")
