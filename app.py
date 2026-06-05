import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
        padding: 18px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .rubric-box {
        background: #f0f4ff;
        border-left: 3px solid #4B6BFB;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .score-chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    .response-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 14px;
        background: #fafafa;
        min-height: 200px;
        font-size: 13px;
        line-height: 1.6;
    }
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
for key in ["scores", "responses", "notes"]:
    if key not in st.session_state:
        st.session_state[key] = {}

MODELS = ["Claude", "ChatGPT", "Gemini", "Llama"]
MODEL_COLORS = {
    "Claude": "#C47B2B",
    "ChatGPT": "#10A37F",
    "Gemini": "#4285F4",
    "Llama": "#7C3AED"
}

SCORE_RUBRIC = {
    1: "Poor — fails to meet the criterion",
    2: "Below average — partial or weak attempt",
    3: "Adequate — meets the criterion at a basic level",
    4: "Good — clearly meets the criterion with minor gaps",
    5: "Excellent — fully meets the criterion with depth and precision"
}

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    use_case_name = st.selectbox("Use case", list(USE_CASES.keys()))
    st.divider()
    st.markdown("**Scoring scale:**")
    for score, label in SCORE_RUBRIC.items():
        color = ["#dc3545","#fd7e14","#ffc107","#28a745","#0d6efd"][score-1]
        st.markdown(f"<span style='color:{color}; font-weight:600'>{score}</span> — {label.split('—')[1].strip()}", unsafe_allow_html=True)
    st.divider()
    st.markdown("**Workflow:**")
    st.markdown("""
1. Copy the prompt (Step 1)
2. Paste all 4 LLM responses (Step 2)
3. Score each response per criterion (Step 3)
4. View the Results Dashboard
5. Export for your paper
    """)
    st.divider()
    st.markdown("**Models:**")
    for m, c in MODEL_COLORS.items():
        st.markdown(f"<span style='color:{c}'>■</span> {m}", unsafe_allow_html=True)

uc = USE_CASES[use_case_name]

# ============ HEADER ============
st.title("📊 LLM Benchmarking Dashboard")
st.caption(f"HELM-inspired evaluation · {use_case_name} · Claude · ChatGPT · Gemini · Llama")

# ============ TABS ============
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Step 1 — Prompt",
    "📝 Step 2 — Responses",
    "⭐ Step 3 — Score",
    "📊 Results & Export"
])

# ======================================================
# TAB 1: PROMPT
# ======================================================
with tab1:
    st.subheader("Use case prompt")
    st.info("Copy this exact prompt and run it in **Claude.ai**, **ChatGPT**, **Gemini**, and **Llama** (llama.com or Perplexity). Then paste each response in Step 2.")

    st.code(uc["prompt"], language=None)

    st.divider()
    st.subheader("Evaluation criteria for this use case")
    cols = st.columns(3)
    for i, (crit, desc) in enumerate(uc["criteria"].items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border:1px solid #e0e0e0; border-radius:8px; padding:12px; margin-bottom:10px; background:#fff;">
                <div style="font-weight:600; font-size:14px; margin-bottom:4px;">{crit}</div>
                <div style="font-size:12px; color:#666;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ======================================================
# TAB 2: RESPONSES
# ======================================================
with tab2:
    st.subheader("Paste the four LLM responses")
    st.caption("Paste each model's exact response to the prompt above. You can save and come back — responses are kept in memory during your session.")

    cols = st.columns(2)
    for i, model in enumerate(MODELS):
        with cols[i % 2]:
            color = MODEL_COLORS[model]
            st.markdown(f"<p style='color:{color}; font-weight:700; font-size:15px; margin-bottom:4px;'>🤖 {model}</p>", unsafe_allow_html=True)
            key = f"{use_case_name}_{model}_response"
            val = st.session_state.responses.get(key, "")
            new_val = st.text_area(
                f"{model} response",
                value=val,
                height=220,
                placeholder=f"Paste {model}'s response here...",
                key=f"ta_{use_case_name}_{model}",
                label_visibility="collapsed"
            )
            st.session_state.responses[key] = new_val
            if new_val.strip():
                wc = len(new_val.split())
                st.caption(f"✅ {wc} words")
            else:
                st.caption("⬆️ Not yet pasted")

    st.divider()
    filled = sum(1 for m in MODELS if (st.session_state.get(f"ta_{use_case_name}_{m}", "") or st.session_state.responses.get(f"{use_case_name}_{m}_response", "")).strip())
    st.progress(filled / 4, text=f"{filled}/4 responses entered — go to Step 3 to score them")

# ======================================================
# TAB 3: SCORING
# ======================================================
with tab3:
    st.subheader("Score each response")
    st.info("""
**How to score:** Read each model's response (shown below), then rate it 1–5 per criterion using the rubric shown next to each slider.
The rubric tells you exactly what to look for — this makes your evaluation rigorous and defensible for your paper.
    """)

    criteria_list = list(uc["criteria"].keys())

    for model in MODELS:
        color = MODEL_COLORS[model]
        # Read from widget state (set by text_area key in Step 2) with fallback to responses dict
        widget_key = f"ta_{use_case_name}_{model}"
        resp_text = (st.session_state.get(widget_key, "") or
                     st.session_state.responses.get(f"{use_case_name}_{model}_response", "")).strip()

        with st.expander(f"🤖 {model}", expanded=True):
            col_resp, col_scores = st.columns([1, 1])

            with col_resp:
                st.markdown("<div class='section-header'>Response</div>", unsafe_allow_html=True)
                if resp_text:
                    st.markdown(f"""
                    <div class="response-card" style="border-top: 3px solid {color};">
                        {resp_text[:1800].replace(chr(10), '<br>')}{'...' if len(resp_text) > 1800 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No response pasted yet — go to Step 2 first.")

            with col_scores:
                st.markdown("<div class='section-header'>Scores (1–5)</div>", unsafe_allow_html=True)
                model_scores = {}
                for crit in criteria_list:
                    crit_desc = uc["criteria"][crit]
                    score_key = f"{use_case_name}_{model}_{crit}"
                    saved = st.session_state.scores.get(score_key, 3)

                    st.markdown(f"""
                    <div class="rubric-box">
                        <strong>{crit}</strong><br>
                        <span style="color:#555;">{crit_desc}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    score = st.select_slider(
                        f"{crit}",
                        options=[1, 2, 3, 4, 5],
                        value=saved,
                        format_func=lambda x: f"{x} — {SCORE_RUBRIC[x].split('—')[1].strip()}",
                        key=f"slider_{use_case_name}_{model}_{crit}",
                        label_visibility="collapsed"
                    )
                    st.session_state.scores[score_key] = score
                    model_scores[crit] = score

                if model_scores:
                    avg = sum(model_scores.values()) / len(model_scores)
                    chip_color = "#28a745" if avg >= 4 else "#ffc107" if avg >= 3 else "#dc3545"
                    st.markdown(f"""
                    <div style="margin-top:12px; text-align:right;">
                        <span class="score-chip" style="background:{chip_color}22; color:{chip_color}; border:1px solid {chip_color}66; font-size:14px; padding:5px 16px;">
                            Average: {avg:.2f} / 5
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                # Optional qualitative note
                note_key = f"{use_case_name}_{model}_note"
                note = st.text_area(
                    "Qualitative observation (optional — use for your paper)",
                    value=st.session_state.notes.get(note_key, ""),
                    height=60,
                    placeholder="e.g. 'Response was fluent but introduced an unsupported refund guarantee'",
                    key=f"note_{use_case_name}_{model}",
                    label_visibility="visible"
                )
                st.session_state.notes[note_key] = note

        st.divider()

# ======================================================
# TAB 4: RESULTS & EXPORT
# ======================================================
with tab4:
    # Check if any scores exist
    all_scores_flat = st.session_state.scores
    has_data = any(
        all_scores_flat.get(f"{uc_n}_{m}_{c}")
        for uc_n, uc_d in USE_CASES.items()
        for m in MODELS
        for c in uc_d["criteria"]
    )

    if not has_data:
        st.info("Score at least one use case in Step 3 to see results here.")
    else:
        # ---- Build score matrix ----
        def get_score(uc_n, model, crit):
            return all_scores_flat.get(f"{uc_n}_{model}_{crit}", None)

        def get_avg(uc_n, model):
            vals = [get_score(uc_n, model, c) for c in USE_CASES[uc_n]["criteria"] if get_score(uc_n, model, c) is not None]
            return round(sum(vals)/len(vals), 2) if vals else None

        def get_overall(model):
            vals = []
            for uc_n, uc_d in USE_CASES.items():
                for c in uc_d["criteria"]:
                    s = get_score(uc_n, model, c)
                    if s is not None:
                        vals.append(s)
            return round(sum(vals)/len(vals), 2) if vals else None

        # ---- Overall Rankings ----
        st.subheader("🏆 Overall Rankings")
        overall_avgs = {m: get_overall(m) for m in MODELS}
        ranked = sorted([(m, v) for m, v in overall_avgs.items() if v is not None], key=lambda x: x[1], reverse=True)

        rank_emojis = ["🥇", "🥈", "🥉", "4️⃣"]
        cols = st.columns(len(ranked))
        for i, (model, avg) in enumerate(ranked):
            with cols[i]:
                color = MODEL_COLORS[model]
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid {color};">
                    <div style="font-size:26px;">{rank_emojis[i]}</div>
                    <div style="font-size:18px; font-weight:700; color:{color}; margin:4px 0;">{model}</div>
                    <div style="font-size:30px; font-weight:800;">{avg:.2f}</div>
                    <div style="color:#888; font-size:12px;">overall avg / 5</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ---- Charts row ----
        col_radar, col_bar = st.columns([1, 1])

        with col_radar:
            st.subheader("📡 Radar — by use case")
            uc_labels = list(USE_CASES.keys())
            short_labels = [u.replace(" ", "\n") for u in uc_labels]
            fig_radar = go.Figure()
            for model in MODELS:
                vals = [get_avg(uc_n, model) or 0 for uc_n in uc_labels]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=short_labels + [short_labels[0]],
                    fill='toself',
                    name=model,
                    line_color=MODEL_COLORS[model],
                    fillcolor=MODEL_COLORS[model],
                    opacity=0.18
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10))),
                showlegend=True,
                height=360,
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(font=dict(size=12))
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_bar:
            st.subheader("📊 Overall average score")
            sorted_models = [m for m, _ in ranked]
            fig_bar = go.Figure(go.Bar(
                x=sorted_models,
                y=[overall_avgs[m] or 0 for m in sorted_models],
                marker_color=[MODEL_COLORS[m] for m in sorted_models],
                text=[f"{overall_avgs[m]:.2f}" for m in sorted_models],
                textposition="outside",
                width=0.5
            ))
            fig_bar.update_layout(
                yaxis=dict(range=[0, 5.8], title="Score (out of 5)"),
                xaxis_title="",
                height=360,
                showlegend=False,
                margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ---- Per use case breakdown ----
        st.subheader("🔍 Breakdown by use case and criterion")

        for uc_n, uc_d in USE_CASES.items():
            crit_keys = list(uc_d["criteria"].keys())
            has_uc_data = any(get_score(uc_n, m, c) is not None for m in MODELS for c in crit_keys)
            if not has_uc_data:
                continue

            with st.expander(f"📁 {uc_n}", expanded=True):
                # Build df
                rows = []
                for c in crit_keys:
                    row = {"Criterion": c}
                    for m in MODELS:
                        row[m] = get_score(uc_n, m, c)
                    rows.append(row)
                df = pd.DataFrame(rows)

                col_tbl, col_chart = st.columns([1, 1.6])

                with col_tbl:
                    def color_score(val):
                        if val is None: return ""
                        if val >= 4: return "background-color:#d4edda; color:#155724"
                        if val >= 3: return "background-color:#fff3cd; color:#856404"
                        return "background-color:#f8d7da; color:#721c24"

                    styled = df.set_index("Criterion").style.map(color_score, subset=MODELS).format("{:.0f}", na_rep="—")
                    st.dataframe(styled, use_container_width=True, height=len(crit_keys)*38+40)

                    # Winner for this use case
                    uc_avgs = {m: get_avg(uc_n, m) for m in MODELS}
                    valid = {m: v for m, v in uc_avgs.items() if v is not None}
                    if valid:
                        winner = max(valid, key=lambda m: valid[m])
                        st.success(f"**Best in this use case:** {winner} ({valid[winner]:.2f}/5)")

                with col_chart:
                    df_melt = df.melt(id_vars="Criterion", var_name="Model", value_name="Score").dropna()
                    fig_uc = px.bar(
                        df_melt, x="Criterion", y="Score", color="Model",
                        barmode="group",
                        color_discrete_map=MODEL_COLORS,
                        text_auto=True
                    )
                    fig_uc.update_layout(
                        yaxis=dict(range=[0, 5.8], title="Score (1–5)"),
                        xaxis_title="",
                        height=300,
                        margin=dict(t=10, b=10),
                        xaxis_tickangle=-25,
                        legend=dict(font=dict(size=11))
                    )
                    st.plotly_chart(fig_uc, use_container_width=True)

                # Qualitative notes
                notes_for_uc = {m: st.session_state.notes.get(f"{uc_n}_{m}_note", "") for m in MODELS}
                if any(notes_for_uc.values()):
                    st.markdown("**Qualitative observations:**")
                    for m, note in notes_for_uc.items():
                        if note.strip():
                            st.markdown(f"<span style='color:{MODEL_COLORS[m]};font-weight:600;'>{m}:</span> {note}", unsafe_allow_html=True)

        st.divider()

        # ---- Full heatmap ----
        st.subheader("🌡️ Complete criteria heatmap")
        heat_rows = []
        y_labels = []
        for uc_n, uc_d in USE_CASES.items():
            for c in uc_d["criteria"]:
                row = [get_score(uc_n, m, c) for m in MODELS]
                heat_rows.append(row)
                y_labels.append(f"{uc_n[:14]}… | {c}")

        fig_heat = go.Figure(go.Heatmap(
            z=heat_rows,
            x=MODELS,
            y=y_labels,
            colorscale=[[0,"#f8d7da"],[0.25,"#fd7e14"],[0.5,"#fff3cd"],[0.75,"#8bc34a"],[1,"#d4edda"]],
            zmin=1, zmax=5,
            text=heat_rows,
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Score", tickvals=[1,2,3,4,5])
        ))
        fig_heat.update_layout(
            height=max(320, len(heat_rows) * 30 + 60),
            margin=dict(l=220, t=20, b=20, r=20),
            xaxis=dict(side="top")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()

        # ---- Export ----
        st.subheader("📄 Export for your paper")

        # Full CSV
        export_rows = []
        for uc_n, uc_d in USE_CASES.items():
            for c in uc_d["criteria"]:
                row = {"Use Case": uc_n, "Criterion": c}
                for m in MODELS:
                    row[m] = get_score(uc_n, m, c) or ""
                export_rows.append(row)
        export_df = pd.DataFrame(export_rows)
        st.dataframe(export_df, use_container_width=True)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download full scores CSV", csv, "llm_benchmark_scores.csv", "text/csv", use_container_width=False)

        # Summary table for paper
        st.markdown("**Summary table (copy into your paper):**")
        summary_rows = []
        for uc_n in USE_CASES:
            row = {"Use Case": uc_n}
            for m in MODELS:
                row[m] = get_avg(uc_n, m) or "—"
            summary_rows.append(row)
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True)
        csv2 = summary_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download summary CSV", csv2, "llm_benchmark_summary.csv", "text/csv")

        # Qualitative notes export
        if any(st.session_state.notes.values()):
            st.divider()
            st.markdown("**Your qualitative observations (for the discussion section):**")
            for uc_n in USE_CASES:
                for m in MODELS:
                    note = st.session_state.notes.get(f"{uc_n}_{m}_note", "")
                    if note.strip():
                        st.markdown(f"- **{uc_n} / {m}:** {note}")

st.divider()
st.caption("LLM Benchmarking Dashboard · Firdaouss El Mouden · Justus-Liebig-Universität Gießen · Zero API cost")
