import streamlit as st
import requests
import json
import pandas as pd

# --- CONFIGURATION ---
API_URL = "/api"

st.set_page_config(page_title="Skylark Agent", page_icon="✈️", layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stChatMessage { padding: 1rem; border-radius: 0.5rem; }
    .stButton button { width: 100%; }
    .status-card { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR STATUS ---
def fetch_status():
    try:
        res = requests.get(f"{API_URL}/status")
        if res.status_code == 200:
            return res.json()
    except:
        return None

status_data = fetch_status()

with st.sidebar:
    st.title("🚁 Skylark Ops")
    
    if status_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Missions", status_data.get("missions", 0))
        with col2:
            st.metric("Pilots Avail", status_data.get("available_pilots", 0))
        
        st.divider()
        st.subheader("Pilot Roster")
        pilots_df = pd.DataFrame(status_data.get("pilots", []))
        if not pilots_df.empty:
            st.dataframe(pilots_df[["name", "location", "status"]], hide_index=True, width='stretch')
            
        st.divider()
        st.subheader("Downloads")
        if st.button("🔄 Refresh Data"):
            st.rerun()
            
        try:
            csv_res = requests.get(f"{API_URL}/csv")
            if csv_res.status_code == 200:
                csv_data = csv_res.json().get("csv_content", "")
                st.download_button(
                    label="📥 Download missions.csv",
                    data=csv_data,
                    file_name="missions.csv",
                    mime="text/csv"
                )
        except:
            st.error("Could not fetch CSV")
    else:
        st.error("Backend offline. Please start FastAPI.")

# --- CHAT INTERFACE ---

st.header("Skylark AI Operations Agent")
st.caption("Powered by Gemini 2.0 Flash • FastAPI Backend")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Skylark. I can help you book drone missions or check the roster. What do you need today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("E.g., Book a mapping drone in Bangalore for next weekend..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare payload
                # Convert 'assistant' -> 'agent' for backend logic if needed, 
                # but backend expects 'role' and 'content' 
                # history_payload = [
                #     {"role": m["role"], "content": m["content"]} 
                #     for m in st.session_state.messages
                # ]
                # In frontend.py
                history_payload = [
    {"role": m["role"], "content": m["content"]} 
    for m in st.session_state.messages[-10:] # Keep only the last 10 messages
]
                
                response = requests.post(
                    f"{API_URL}/chat", 
                    json={"history": history_payload, "user_input": prompt}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_text = data.get("text", "")
                    action_data = data.get("action_taken")
                    
                    st.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                    
                    if action_data:
                        st.success(f"Booking confirmed! Token: {action_data.get('bookingToken')}")
                        st.rerun() # Refresh to update sidebar numbers
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:

                st.error(f"Connection Failed: {e}")
