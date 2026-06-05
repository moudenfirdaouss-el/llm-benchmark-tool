import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from use_cases import USE_CASES

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Free LLM Benchmarking Tool",
    page_icon="📊",
    layout="wide"
)

# ============ SESSION STATE ============
if "results_df" not in st.session_state:
    st.session_state.results_df = None

# ============ HEADER ============
st.title("📊 LLM Research Dashboard (Manual Entry)")
st.caption("A tool for researchers to organize and visualize comparisons between Claude, ChatGPT, and Gemini.")

st.markdown("""
**Instructions for Free Version:**
1. Select a use case.
2. Go to the free websites (**Claude.ai**, **ChatGPT**, and **Gemini**) and run the prompt.
3. Copy their responses and paste them into the boxes below.
4. Rate them from 1-10 based on your own observation.
5. Click **'Generate Comparison Report'**.
""")

# ============ SIDEBAR ============
st.sidebar.header("⚙️ Research Settings")
use_case_name = st.sidebar.selectbox("Select Use Case", list(USE_CASES.keys()))
use_case = USE_CASES[use_case_name]

# ============ STEP 1: PROMPT PREVIEW ============
with st.expander("📝 View Prompt to be used on AI Websites", expanded=True):
    st.text_area("Copy this prompt:", use_case["prompt"], height=150)

# ============ STEP 2: DATA ENTRY ============
st.header("Step 1: Input AI Responses & Scores")
st.info("After running the prompt on the respective websites, paste the text and assign a score (1-10) for each metric.")

col1, col2, col3 = st.columns(3)

def input_section(col, model_name):
    with col:
        st.subheader(f"🤖 {model_name}")
        resp = st.text_area(f"{model_name} Response:", height=150, key=f"text_{model_name}")
        st.write(f"**Assign Scores (1-10)**")
        s1 = st.slider("Factual Integrity", 1, 10, 5, key=f"s1_{model_name}")
        s2 = st.slider("Constraint Adherence", 1, 10, 5, key=f"s2_{model_name}")
        s3 = st.slider("Reasoning Transparency", 1, 10, 5, key=f"s3_{model_name}")
        s4 = st.slider("Fairness & Bias", 1, 10, 5, key=f"s4_{model_name}")
        s5 = st.slider("Practical Utility", 1, 10, 5, key=f"s5_{model_name}")
        return {"model": model_name, "text": resp, "scores": [s1, s2, s3, s4, s5]}

claude_data = input_section(col1, "Claude")
chatgpt_data = input_section(col2, "ChatGPT")
gemini_data = input_section(col3, "Gemini")

# ============ STEP 3: GENERATE REPORT ============
if st.button("🚀 Generate Comparison Report", type="primary"):
    metrics = ["Factual Integrity", "Constraint Adherence", "Reasoning", "Fairness", "Utility"]
    
    data = {
        "Metric": metrics * 3,
        "Claude": [claude_data["scores"][0], claude_data["scores"][1], claude_data["scores"][2], claude_data["scores"][3], claude_data["scores"][4]],
        "ChatGPT": [chatgpt_data["scores"][0], chatgpt_data["scores"][1], chatgpt_data["scores"][2], chatgpt_data["scores"][3], chatgpt_data["scores"][4]],
        "Gemini": [gemini_data["scores"][0], gemini_data["scores"][1], gemini_data["scores"][2], gemini_data["scores"][3], gemini_data["scores"][4]],
    }
    
    # Re-formatting for a clean table
    rows = []
    for i, m in enumerate(metrics):
        rows.append({"Metric": m, "Claude": claude_data["scores"][i], "ChatGPT": chatgpt_data["scores"][i], "Gemini": gemini_data["scores"][i]})
    
    st.session_state.results_df = pd.DataFrame(rows)

# ============ STEP 4: VISUALIZATION ============
if st.session_state.results_df is not None:
    st.divider()
    st.header("📊 Research Results")
    
    df = st.session_state.results_df
    
    # Display Table
    st.subheader("Score Summary Table")
    st.dataframe(df, use_container_width=True)
    
    # Grouped Bar Chart
    st.subheader("Side-by-Side Metric Comparison")
    # Melt the dataframe to make it "Long Format" for Plotly
    df_melted = df.melt(id_vars="Metric", var_name="Model", value_name="Score")
    
    fig = px.bar(
        df_melted, 
        x="Metric", 
        y="Score", 
        color="Model", 
        barmode="group",
        color_discrete_map={"Claude": "#D97757", "ChatGPT": "#10A37F", "Gemini": "#4285F4"}
    )
    fig.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results as CSV", csv, "llm_research_results.csv", "text/csv")

st.markdown("---")
st.caption("Built for manual research | No API costs | Data stays in your browser")
