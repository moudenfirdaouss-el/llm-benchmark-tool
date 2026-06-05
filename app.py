import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import anthropic
import json
import re
from use_cases import USE_CASES

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="LLM Benchmarking Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .winner-card {
        background: linear-gradient(135deg, #fff8e1, #fff3cd);
        border: 2px solid #ffc107;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .rank-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "analysis" not in st.session_state:
    st.session_state.analysis = {}
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "scored" not in st.session_state:
    st.session_state.scored = False

MODELS = ["Claude", "ChatGPT", "Gemini", "Llama"]
MODEL_COLORS = {
    "Claude": "#C47B2B",
    "ChatGPT": "#10A37F",
    "Gemini": "#4285F4",
    "Llama": "#7C3AED"
}

# ============ HEADER ============
st.title("📊 LLM Benchmarking Dashboard")
st.caption("HELM-inspired evaluation of Claude · ChatGPT · Gemini · Llama across three business use cases")

# ============ SIDEBAR ============
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Anthropic API Key", type="password",
                             help="Required for AI-powered auto-scoring. Get one at console.anthropic.com")
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("""
1. Select a use case
2. Copy the prompt → run in each LLM
3. Paste all four responses
4. Click **Auto-Score** (uses Claude to evaluate)
5. View the full results dashboard
    """)
    st.divider()
    st.markdown("**Models compared:**")
    for m, c in MODEL_COLORS.items():
        st.markdown(f"<span style='color:{c}'>■</span> {m}", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["📝 Input & Scoring", "📊 Results Dashboard", "📄 Export Report"])

# ============ TAB 1: INPUT ============
with tab1:
    use_case_name = st.selectbox("Select Use Case", list(USE_CASES.keys()),
                                  help="Each use case uses its own domain-specific evaluation criteria")
    uc = USE_CASES[use_case_name]

    with st.expander("📋 Prompt to run in each LLM", expanded=True):
        st.code(uc["prompt"], language=None)
        st.caption("Copy this exact prompt and run it in Claude.ai, ChatGPT, Gemini, and Llama.")

    with st.expander("🎯 Evaluation criteria for this use case", expanded=False):
        cols = st.columns(len(uc["criteria"]))
        for i, (c, desc) in enumerate(uc["criteria"].items()):
            with cols[i]:
                st.markdown(f"**{c}**")
                st.caption(desc)

    st.subheader("Paste LLM Responses")
    st.info("Paste each model's response below. Claude's response will be generated automatically if you provide an API key and leave it blank.")

    response_inputs = {}
    cols = st.columns(4)
    for i, model in enumerate(MODELS):
        with cols[i]:
            color = MODEL_COLORS[model]
            st.markdown(f"<p style='color:{color}; font-weight:600; font-size:16px;'>🤖 {model}</p>", unsafe_allow_html=True)
            if model == "Claude":
                st.caption("Leave blank to auto-generate via API")
            response_inputs[model] = st.text_area(
                f"{model} response",
                value=st.session_state.responses.get(f"{use_case_name}_{model}", ""),
                height=200,
                key=f"resp_{use_case_name}_{model}",
                label_visibility="collapsed"
            )

    st.divider()
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        score_btn = st.button("🚀 Auto-Score All", type="primary", use_container_width=True,
                              help="Uses Claude via API to score each response on all criteria")
    with col_btn2:
        if not api_key:
            st.warning("⚠️ Add your Anthropic API key in the sidebar to enable auto-scoring.")

    if score_btn:
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
        else:
            client = anthropic.Anthropic(api_key=api_key)
            progress = st.progress(0, text="Starting evaluation...")
            total = len(MODELS)

            for idx, model in enumerate(MODELS):
                progress.progress((idx) / total, text=f"Scoring {model}...")
                resp_text = response_inputs[model].strip()

                # Auto-generate Claude's response if blank
                if model == "Claude" and not resp_text:
                    with st.spinner("Generating Claude's response..."):
                        gen = client.messages.create(
                            model="claude-opus-4-5",
                            max_tokens=800,
                            messages=[{"role": "user", "content": uc["prompt"]}]
                        )
                        resp_text = gen.content[0].text
                        st.session_state.responses[f"{use_case_name}_Claude"] = resp_text

                if not resp_text:
                    st.warning(f"No response for {model} — skipping.")
                    continue

                # Build scoring prompt
                criteria_str = "\n".join([f"- {k}: {v}" for k, v in uc["criteria"].items()])
                score_prompt = f"""You are a rigorous AI evaluation expert applying HELM-inspired methodology.

Use case: {use_case_name}
Scoring criteria (rate each 1–5):
{criteria_str}

Response to evaluate (from {model}):
\"\"\"{resp_text[:1500]}\"\"\"

Return ONLY a valid JSON object with these exact keys and integer scores 1-5:
{json.dumps({k: 0 for k in uc["criteria"].keys()})}

No explanation. No markdown. Only the JSON."""

                try:
                    result = client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=500,
                        messages=[{"role": "user", "content": score_prompt}]
                    )
                    raw = result.content[0].text.strip()
                    raw = re.sub(r"```json|```", "", raw).strip()
                    parsed = json.loads(raw)
                    st.session_state.scores[f"{use_case_name}_{model}"] = parsed
                except Exception as e:
                    st.error(f"Scoring failed for {model}: {e}")

            # Generate narrative analysis
            progress.progress(0.9, text="Generating analysis...")
            score_summary = ""
            for model in MODELS:
                key = f"{use_case_name}_{model}"
                if key in st.session_state.scores:
                    s = st.session_state.scores[key]
                    avg = sum(s.values()) / len(s)
                    score_summary += f"\n{model}: avg {avg:.1f}/5, detail: {s}"

            analysis_prompt = f"""You are an AI benchmarking expert writing for an academic seminar paper.

Use case: {use_case_name}
Scores:{score_summary}

Write a concise analytical paragraph (5–6 sentences) comparing the four LLMs on this use case. 
Mention which model performed best and why, note specific strengths and weaknesses by criterion, 
and give a business deployment recommendation. Be specific and data-driven."""

            try:
                ana = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=500,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                st.session_state.analysis[use_case_name] = ana.content[0].text
            except Exception as e:
                st.session_state.analysis[use_case_name] = f"Analysis generation failed: {e}"

            progress.progress(1.0, text="Done!")
            st.session_state.scored = True
            st.success("✅ Scoring complete! Go to the Results Dashboard tab.")
            st.rerun()

# ============ TAB 2: RESULTS ============
with tab2:
    all_scores = st.session_state.scores
    if not all_scores:
        st.info("Run auto-scoring in the Input tab first to see results here.")
    else:
        # ---- Overall scores across all use cases ----
        st.subheader("🏆 Overall Rankings")

        overall = {m: [] for m in MODELS}
        for key, scores_dict in all_scores.items():
            for m in MODELS:
                if key.endswith(f"_{m}"):
                    overall[m].extend(scores_dict.values())

        overall_avg = {m: (sum(v)/len(v) if v else 0) for m, v in overall.items()}
        ranked = sorted(overall_avg.items(), key=lambda x: x[1], reverse=True)

        rank_emojis = ["🥇", "🥈", "🥉", "4️⃣"]
        cols = st.columns(4)
        for i, (model, avg) in enumerate(ranked):
            with cols[i]:
                color = MODEL_COLORS[model]
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid {color};">
                    <div style="font-size:28px">{rank_emojis[i]}</div>
                    <div style="font-size:20px; font-weight:700; color:{color}">{model}</div>
                    <div style="font-size:32px; font-weight:800">{avg:.2f}</div>
                    <div style="color:#888; font-size:13px">overall avg / 5</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ---- Radar chart ----
        col_radar, col_bar = st.columns([1, 1])

        with col_radar:
            st.subheader("📡 Radar — by Use Case")
            use_case_avgs = {m: [] for m in MODELS}
            uc_labels = []
            for uc_name in USE_CASES.keys():
                uc_labels.append(uc_name.replace(" ", "\n"))
                for m in MODELS:
                    key = f"{uc_name}_{m}"
                    if key in all_scores:
                        s = all_scores[key]
                        use_case_avgs[m].append(round(sum(s.values())/len(s), 2))
                    else:
                        use_case_avgs[m].append(0)

            fig_radar = go.Figure()
            for model in MODELS:
                vals = use_case_avgs[model]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=uc_labels + [uc_labels[0]],
                    fill='toself',
                    name=model,
                    line_color=MODEL_COLORS[model],
                    fillcolor=MODEL_COLORS[model],
                    opacity=0.2
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=True,
                height=380,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_bar:
            st.subheader("📊 Overall Average Score")
            fig_bar = go.Figure()
            sorted_models = [m for m, _ in ranked]
            fig_bar.add_trace(go.Bar(
                x=sorted_models,
                y=[overall_avg[m] for m in sorted_models],
                marker_color=[MODEL_COLORS[m] for m in sorted_models],
                text=[f"{overall_avg[m]:.2f}" for m in sorted_models],
                textposition="outside"
            ))
            fig_bar.update_layout(
                yaxis=dict(range=[0, 5.5], title="Average Score (out of 5)"),
                xaxis_title="",
                height=380,
                showlegend=False,
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ---- Per use case breakdown ----
        st.subheader("🔍 Breakdown by Use Case & Criteria")

        for uc_name, uc_data in USE_CASES.items():
            keys_present = [f"{uc_name}_{m}" for m in MODELS if f"{uc_name}_{m}" in all_scores]
            if not keys_present:
                continue

            with st.expander(f"📁 {uc_name}", expanded=True):
                criteria_list = list(uc_data["criteria"].keys())

                # Build DataFrame
                rows = []
                for criterion in criteria_list:
                    row = {"Criterion": criterion}
                    for m in MODELS:
                        key = f"{uc_name}_{m}"
                        row[m] = all_scores.get(key, {}).get(criterion, None)
                    rows.append(row)
                df = pd.DataFrame(rows)

                col_tbl, col_chart = st.columns([1, 1.5])

                with col_tbl:
                    # Styled table
                    def color_score(val):
                        if val is None:
                            return ""
                        if val >= 4:
                            return "background-color: #d4edda; color: #155724"
                        elif val >= 3:
                            return "background-color: #fff3cd; color: #856404"
                        else:
                            return "background-color: #f8d7da; color: #721c24"

                    styled = df.set_index("Criterion").style.applymap(
                        color_score, subset=MODELS
                    ).format("{:.0f}", na_rep="—")
                    st.dataframe(styled, use_container_width=True)

                with col_chart:
                    # Grouped bar chart per criterion
                    df_melt = df.melt(id_vars="Criterion", var_name="Model", value_name="Score").dropna()
                    fig_uc = px.bar(
                        df_melt, x="Criterion", y="Score", color="Model",
                        barmode="group",
                        color_discrete_map=MODEL_COLORS,
                        text_auto=True
                    )
                    fig_uc.update_layout(
                        yaxis=dict(range=[0, 5.5], title="Score (1–5)"),
                        xaxis_title="",
                        legend_title="Model",
                        height=280,
                        margin=dict(t=10, b=10),
                        xaxis_tickangle=-20
                    )
                    st.plotly_chart(fig_uc, use_container_width=True)

                # Narrative analysis
                if uc_name in st.session_state.analysis:
                    st.markdown("**🧠 AI-generated analysis:**")
                    st.info(st.session_state.analysis[uc_name])

        st.divider()

        # ---- Heatmap ----
        st.subheader("🌡️ Full Criteria Heatmap (all use cases)")
        heat_rows = []
        for uc_name, uc_data in USE_CASES.items():
            for criterion in uc_data["criteria"].keys():
                row = {"Use Case + Criterion": f"{uc_name[:12]}… | {criterion}"}
                for m in MODELS:
                    key = f"{uc_name}_{m}"
                    row[m] = all_scores.get(key, {}).get(criterion, None)
                heat_rows.append(row)

        heat_df = pd.DataFrame(heat_rows).set_index("Use Case + Criterion")
        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_df[MODELS].values.tolist(),
            x=MODELS,
            y=heat_df.index.tolist(),
            colorscale=[[0, "#f8d7da"], [0.5, "#fff3cd"], [1, "#d4edda"]],
            zmin=1, zmax=5,
            text=heat_df[MODELS].values.tolist(),
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Score")
        ))
        fig_heat.update_layout(height=max(300, len(heat_rows) * 28), margin=dict(l=200, t=10, b=10))
        st.plotly_chart(fig_heat, use_container_width=True)

# ============ TAB 3: EXPORT ============
with tab3:
    st.subheader("📄 Export Report")
    if not st.session_state.scores:
        st.info("Score some use cases first to export results.")
    else:
        # Build full summary table
        all_rows = []
        for uc_name, uc_data in USE_CASES.items():
            for criterion in uc_data["criteria"].keys():
                row = {"Use Case": uc_name, "Criterion": criterion}
                for m in MODELS:
                    key = f"{uc_name}_{m}"
                    row[m] = st.session_state.scores.get(key, {}).get(criterion, "")
                all_rows.append(row)

        export_df = pd.DataFrame(all_rows)
        st.dataframe(export_df, use_container_width=True)

        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Scores CSV", csv, "llm_benchmark_scores.csv", "text/csv")

        # Summary for paper
        st.divider()
        st.subheader("📝 Use in your paper")
        st.markdown("**Copy the analysis paragraphs below into your seminar paper:**")
        for uc_name, text in st.session_state.analysis.items():
            st.markdown(f"**{uc_name}**")
            st.text_area("", text, height=120, key=f"export_{uc_name}", label_visibility="collapsed")

st.divider()
st.caption("Built for academic LLM benchmarking | Firdaouss El Mouden | Justus-Liebig-Universität Gießen")
