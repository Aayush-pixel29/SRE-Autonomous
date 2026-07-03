import sys
import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize the shared local intelligence engine
llm = ChatOllama(model="llama3.1", temperature=0.0)

# --- Agent 1: Infrastructure Specialist ---
def run_sre_agent(task_description: str) -> str:
    print("🤖 [Swarm] Activating Infrastructure SRE Agent...")
    system_prompt = (
        "You are an elite DevOps & Infrastructure Engineer.\n"
        "Your job is to analyze system metrics and propose a technical fix.\n"
        "Respond ONLY with the technical root cause and technical resolution details."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=task_description)
    ]
    response = llm.invoke(messages)
    return response.content

# --- Agent 2: FinOps Business Analyst ---
def run_finops_agent(proposed_fix: str, budget_limit: str) -> str:
    print("💰 [Swarm] Activating FinOps Cost Analyst Agent...")
    system_prompt = (
        f"You are a FinOps Cloud Cost Architect. Your strict allocation budget threshold is {budget_limit}.\n"
        "Evaluate the proposed technical fix. If upgrading resources exceeds the budget, flag a 'CRITICAL_BUDGET_VIOLATION' "
        "and suggest a zero-cost optimization alternative (like code profiling or connection scaling).\n"
        "Respond with a clear approval status and cost breakdown."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Proposed Technical Fix: {proposed_fix}")
    ]
    response = llm.invoke(messages)
    return response.content

# --- Swarm Supervisor Orchestrator ---
def run_enterprise_swarm(incident_query: str, budget: str):
    print(f"🚀 [Supervisor] Initializing Swarm Triage Protocol...")
    
    # Step 1: Delegate system diagnostics to the SRE Agent
    sre_verdict = run_sre_agent(incident_query)
    print(f"\n[SRE Agent Verdict]:\n{sre_verdict}\n")
    print("-" * 40)
    
    # Step 2: Pass SRE's technical strategy to the FinOps Agent for fiscal compliance vetting
    finops_verdict = run_finops_agent(proposed_fix=sre_verdict, budget_limit=budget)
    print(f"\n[FinOps Agent Verdict]:\n{finops_verdict}\n")
    print("-" * 40)
    
    # Step 3: Synthesis Turn
    print("📝 [Supervisor] Compiling Final Operational Summary...")
    synthesis_prompt = (
        "You are the Swarm Supervisor. Synthesize the reports from the SRE Agent and the FinOps Agent "
        "into a single execution ticket for the engineering team. Balance tech stability with cost constraints."
    )
    final_messages = [
        SystemMessage(content=synthesis_prompt),
        HumanMessage(content=f"SRE Report: {sre_verdict}\n\nFinOps Report: {finops_verdict}")
    ]
    final_ticket = llm.invoke(final_messages)
    return final_ticket.content

if __name__ == "__main__":
    # Context Scenario: The checkout service crashed out of memory. 
    # SRE will want to double memory allocation, but let's see how FinOps reacts under a strict $50 budget limit.
    sample_incident = "The checkout_service crashed with an OOMKilled error code under a 94% transaction spike load."
    allocated_budget = "$50 remaining cloud budget threshold"
    
    final_resolution_ticket = run_enterprise_swarm(sample_incident, allocated_budget)
    
    print("\n================ FINAL SWARM RESOLUTION TICKET ================")
    print(final_resolution_ticket)
