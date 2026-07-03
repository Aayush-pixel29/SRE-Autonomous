import streamlit as st
import requests

st.set_page_config(page_title="SRE Autonomous Swarm Ops", layout="wide")

st.title("🔍 SRE Autonomous Swarm Control Center")
st.caption("Enterprise Infrastructure Log Ingestion & Threat Analysis Engine")

# Workspace Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Execute Diagnostic Pipeline")
    user_query = st.text_input(
        "Enter system incident or telemetry query:",
        placeholder="What caused the checkout_service to crash?"
    )
    
    if st.button("Trigger Autonomous Triage", type="primary"):
        if user_query:
            with st.spinner("Swarm Agent analyzing telemetry clusters..."):
                try:
                    # Call our local FastAPI endpoint
                    res = requests.post(
                        "http://localhost:8000/api/triage", 
                        json={"query": user_query}
                    )
                    data = res.json()
                    
                    st.success("Analysis Complete!")
                    st.markdown("### 📝 Agent Resolution Feedback")
                    st.markdown(data["answer"])
                    
                    # Store metrics inside state for side column parsing
                    st.session_state["last_metrics"] = data["telemetry"]
                    
                except Exception as e:
                    st.error(f"Failed to connect to triage backend services: {e}")
        else:
            st.warning("Please input a valid system operational trace prompt.")

with col2:
    st.subheader("📊 Live Pipeline Telemetry")
    if "last_metrics" in st.session_state:
        metrics = st.session_state["last_metrics"]
        
        st.metric(label="Inference Latency", value=f"{metrics['latency_ms']} ms")
        
        st.markdown("---")
        st.markdown("**Token Consumption Footprint**")
        st.json({
            "Prompt Tokens": metrics["prompt_tokens"],
            "Completion Tokens": metrics["completion_tokens"],
            "Estimated Cost (Local)": "$0.0000 (Local Hardware Residency)"
        })
    else:
        st.info("Awaiting pipeline trigger initialization to capture telemetry vectors.")
