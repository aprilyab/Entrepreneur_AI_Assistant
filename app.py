# app.py
import streamlit as st
from src.graph import EntrepreneurGraph

st.set_page_config(page_title="Entrepreneur AI Assistant", layout="wide")
st.title("🚀 Entrepreneur AI Assistant")

# Initialize EntrepreneurGraph in session state
if "graph" not in st.session_state:
    st.session_state.graph = EntrepreneurGraph(session_id="001", user_name="Henok")

graph: EntrepreneurGraph = st.session_state.graph

# Step 1: Get user idea
idea_text = st.text_input("Enter your startup idea:", key="idea_input")

if st.button("Generate Business Plan") and idea_text.strip():
    with st.spinner("Generating business plan..."):
        final_state = graph.run(idea_text)

    st.subheader("💡 Your Idea")
    st.write(getattr(final_state, "idea", "[No idea provided]"))

    st.subheader("ℹ️ Optional Info / Follow-ups")
    st.write(getattr(final_state, "extra_info", "[No extra info]"))

    st.subheader("📊 Market Analysis")
    st.write(getattr(final_state, "market_analysis", "[No market analysis]"))

    st.subheader("🏗️ Business Model")
    st.write(getattr(final_state, "business_model", "[No business model]"))

    st.subheader("✅ Validation Strategy")
    st.write(getattr(final_state, "validation_strategy", "[No validation strategy]"))

    st.subheader("⚠️ Risks")
    st.write(getattr(final_state, "risks", "[No risks]"))

    st.subheader("💰 Financials")
    st.write(getattr(final_state, "financials", "[No financials]"))

    st.subheader("📄 Full Business Plan")
    st.write(getattr(final_state, "full_plan", "[No plan generated]"))
