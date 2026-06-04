import streamlit as st
import anthropic
import pandas as pd
import plotly.graph_objects as go
from use_cases import USE_CASES
from evaluator import EVALUATION_PROMPT, PAIRWISE_PROMPT, parse_json_response

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="LLM Benchmark Tool",
    page_icon="🔬",
    layout="wide"
)

# ============ API CLIENT ============
@st.cache_resource
def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

client = get_client()
MODEL = "claude-sonnet-4-20250514"

# ============ SESSION STATE ============
if "claude_response" not in st.session_state:
    st.session_state.claude_response = ""
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None
if "pairwise_results" not in st.session_state:
    st.session_state.pairwise_results = None

# ============ HEADER ============
st.title("🔬 HELM-Inspired LLM Benchmarking Tool")
st.caption("Compare Claude, ChatGPT, and Gemini across three business use cases")

st.markdown("""
**Methodology:** This tool draws inspiration from Stanford's HELM framework 
(multi-metric evaluation) and LMSYS's MT-Bench (LLM-as-a-Judge pairwise comparison).
""")

# ============ SIDEBAR ============
st.sidebar.header("⚙️ Configuration")
use_case_name = st.sidebar.selectbox("Select Use Case", list(USE_CASES.keys()))
eval_mode = st.sidebar.radio(
    "Evaluation Mode",
    ["Absolute Scoring (HELM)", "Pairwise Comparison (MT-Bench)", "Both"]
)

use_case = USE_CASES[use_case_name]

# ============ STEP 1: SHOW PROMPT ============
st.header("Step 1: Review the Prompt")
st.text_area("Prompt sent to all LLMs:", use_case["prompt"], height=200, disabled=True)

# ============ STEP 2: RUN CLAUDE LIVE ============
st.header("Step 2: Run Claude (Live API)")

if st.button("🚀 Run Claude", type="primary"):
    with st.spinner("Querying Claude..."):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": use_case["prompt"]}]
            )
            st.session_state.claude_response = response.content[0].text
            st.success("✅ Claude responded!")
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.claude_response:
    st.text_area("Claude's Response:", st.session_state.claude_response, height=250)

# ============ STEP 3: PASTE OTHER RESPONSES ============
st.header("Step 3: Paste Responses from ChatGPT and Gemini")

col1, col2 = st.columns(2)
with col1:
    chatgpt_response = st.text_area("ChatGPT Response:", height=250, key="chatgpt")
with col2:
    gemini_response = st.text_area("Gemini Response:", height=250, key="gemini")

# ============ STEP 4: EVALUATE ============
st.header("Step 4: Run Evaluation")

if st.button("🎯 Evaluate All Responses", type="primary"):
    if not st.session_state.claude_response or not chatgpt_response or not gemini_response:
        st.warning("⚠️ Please provide all three responses before evaluating.")
    else:
        # ABSOLUTE SCORING
        if eval_mode in ["Absolute Scoring (HELM)", "Both"]:
            with st.spinner("Running absolute scoring..."):
                eval_prompt = EVALUATION_PROMPT.format(
                    use_case=use_case_name,
                    focus=use_case["focus"],
                    response_a=st.session_state.claude_response,
                    response_b=chatgpt_response,
                    response_c=gemini_response
                )
                try:
                    result = client.messages.create(
                        model=MODEL,
                        max_tokens=3000,
                        messages=[{"role": "user", "content": eval_prompt}]
                    )
                    parsed = parse_json_response(result.content[0].text)
                    st.session_state.evaluation_results = parsed
                except Exception as e:
                    st.error(f"Evaluation error: {e}")

        # PAIRWISE COMPARISON
        if eval_mode in ["Pairwise Comparison (MT-Bench)", "Both"]:
            with st.spinner("Running pairwise comparisons..."):
                pairs = [
                    ("Claude", st.session_state.claude_response, "ChatGPT", chatgpt_response),
                    ("Claude", st.session_state.claude_response, "Gemini", gemini_response),
                    ("ChatGPT", chatgpt_response, "Gemini", gemini_response),
                ]
                pairwise_results = []
                for name_a, resp_a, name_b, resp_b in pairs:
                    p_prompt = PAIRWISE_PROMPT.format(
                        use_case=use_case_name,
                        original_prompt=use_case["prompt"],
                        name_a=name_a,
                        response_a=resp_a,
                        name_b=name_b,
                        response_b=resp_b
                name_b}"
                            pairwise_results.append(parsed)
                    except Exception as e:
                        st.error(f"Pairwise error: {e}")
                st.session_state.pairwise_results = pairwise_results

# ============ STEP 5: RESULTS ============
if st.session_state.evaluation_results:
    st.header("📊 Absolute Scoring Results")
    results = st.session_state.evaluation_results
    
    # Build dataframe
    metrics = ["Factual Integrity", "Constraint Adherence", "Reasoning Transparency", 
               "Fairness & Bias", "Practical Utility"]
    metric_keys = ["factual_integrity", "constraint_adher][k] for k in metric_keys],
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Radar chart
        fig = go.Figure()
        for llm in ["Claude", "ChatGPT", "Gemini"]:
            fig.add_trace(go.Scatterpolar(
                r=df[llm].tolist() + [df[llm].tolist()[0]],
                theta=metrics + [metrics[0]],
                fill='toself',
                name=llm
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            title="HELM-Inspired Multi-Metric Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary
        st.subheader("📝 Summary")
        st.info(results.get("summary", "No summary provided."))
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Results (CSV)", csv, "benchmark_results.csv")
    
    except Exception as e:
        st.error(f"Could not parse results: {e}")
        st.json(results)

if st.session_state.pairwise_results:
    st.header("⚔️ Pairwise Comparison Results (MT-B', 'N/A')}")
            st.write(f"**Key Differentiator:** {match.get('key_differentiator', 'N/A')}")
    
    # Win counts
    win_counts = {"Claude": 0, "ChatGPT": 0, "Gemini": 0, "Tie": 0}
    for match in st.session_state.pairwise_results:
        winner = match.get("winner", "Tie")
        if winner in win_counts:
            win_counts[winner] += 1
    
    st.subheader("🏆 Overall Win Count")
    win_df = pd.DataFrame(list(win_counts.items()), columns=["LLM", "Wins"])
    st.bar_chart(win_df.set_index("LLM"))

# ============ FOOTER ============
st.markdown("---")
st.caption("Built with Streamlit | Powered by Claude API | Methodology: HELM + MT-Bench")
