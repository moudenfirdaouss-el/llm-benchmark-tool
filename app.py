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
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.2);
    }
    .rubric-box {
        border-left: 3px solid #4B6BFB;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 13px;
        opacity: 0.9;
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
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        padding: 14px;
        background: transparent;
        min-height: 200px;
        max-height: 420px;
        overflow-y: auto;
        font-size: 13px;
        line-height: 1.7;
        color: inherit;
    }
    .crit-card {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.55;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============ PERSISTENCE (JSON file) ============
import json, os

SAVE_FILE = "benchmark_data.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"scores": {}, "responses": {}, "notes": {}}

def save_data():
    data = {
        "scores":    dict(st.session_state.scores),
        "responses": dict(st.session_state.responses),
        "notes":     dict(st.session_state.notes),
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============ SESSION STATE ============
if "scores" not in st.session_state:
    _saved = load_data()
    st.session_state.scores    = _saved["scores"]
    st.session_state.responses = _saved["responses"]
    st.session_state.notes     = _saved["notes"]

MODELS = ["Claude", "ChatGPT", "Gemini", "Deepseek"]
MODEL_COLORS = {
    "Claude":   "#C47B2B",
    "ChatGPT":  "#10A37F",
    "Gemini":   "#4285F4",
    "Deepseek":    "#7C3AED"
}

SCORE_RUBRIC = {
    1: "Poor — fails to meet the criterion",
    2: "Below average — partial or weak attempt",
    3: "Adequate — meets the criterion at a basic level",
    4: "Good — clearly meets the criterion with minor gaps",
    5: "Excellent — fully meets the criterion with depth and precision"
}

RANK_COLORS = ["#B8860B", "#708090", "#8B4513", "#555555"]

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    use_case_name = st.selectbox("Use case", list(USE_CASES.keys()))
    st.divider()
    st.markdown("**Scoring scale (1–5):**")
    scale_colors = ["#dc3545", "#fd7e14", "#ffc107", "#28a745", "#0d6efd"]
    for score, label in SCORE_RUBRIC.items():
        c = scale_colors[score - 1]
        desc = label.split("—")[1].strip()
        st.markdown(
            f"<span style='color:{c}; font-weight:700'>{score}</span>"
            f" <span style='font-size:12px; opacity:0.8'>— {desc}</span>",
            unsafe_allow_html=True
        )
    st.divider()
    st.markdown("**Workflow:**")
    st.markdown("""
1. Copy the prompt → Step 1
2. Paste all 4 responses → Step 2
3. Rate each response → Step 3
4. View charts & rankings → Step 4
5. Export CSV for your paper
    """)
    st.divider()
    st.markdown("**Models:**")
    for m, c in MODEL_COLORS.items():
        st.markdown(f"<span style='color:{c}; font-size:16px'>■</span> {m}", unsafe_allow_html=True)
    st.divider()
    if st.button("🗑️ Clear all saved data", use_container_width=True):
        st.session_state.scores    = {}
        st.session_state.responses = {}
        st.session_state.notes     = {}
        save_data()
        st.success("All data cleared.")
        st.rerun()

uc = USE_CASES[use_case_name]

# ============ HEADER ============
st.title("📊 LLM Benchmarking Dashboard")
st.caption(
    f"HELM-inspired evaluation · **{use_case_name}** · "
    "Claude · ChatGPT · Gemini · Deepseek · Zero API cost"
)

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Step 1 — Prompt",
    "📝 Step 2 — Responses",
    "⭐ Step 3 — Score",
    "📊 Step 4 — Results & Export",
    "🧠 Hallucination Analysis"
])

# ======================================================
# TAB 1: PROMPT
# ======================================================
with tab1:
    st.subheader("Prompt to run in each LLM")
    st.info(
        "Copy this exact prompt and run it in **Claude.ai**, **ChatGPT**, **Gemini**, "
        "and **Deepseek**  Then paste each response in Step 2."
    )
    st.code(uc["prompt"], language=None)

    st.divider()
    st.subheader("Evaluation criteria for this use case")
    cols = st.columns(3)
    for i, (crit, desc) in enumerate(uc["criteria"].items()):
        with cols[i % 3]:
            st.markdown(
                f"<div class='crit-card'>"
                f"<div style='font-weight:600; font-size:14px; margin-bottom:4px;'>{crit}</div>"
                f"<div style='font-size:12px; opacity:0.7;'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

# ======================================================
# TAB 2: RESPONSES
# ======================================================
with tab2:
    st.subheader("Paste the four LLM responses")
    st.caption(
        "Paste each model's exact response to the prompt above. "
        "Responses are kept in memory for the full session."
    )

    cols = st.columns(2)
    for i, model in enumerate(MODELS):
        with cols[i % 2]:
            color = MODEL_COLORS[model]
            st.markdown(
                f"<p style='color:{color}; font-weight:700; font-size:15px; margin-bottom:2px;'>"
                f"🤖 {model}</p>",
                unsafe_allow_html=True
            )
            persist_key = f"resp_{use_case_name}_{model}"
            saved_val = st.session_state.responses.get(persist_key, "")

            new_val = st.text_area(
                label=f"{model} response",
                value=saved_val,
                height=240,
                placeholder=f"Paste {model}'s response here...",
                key=f"ta_{use_case_name}_{model}",
                label_visibility="collapsed"
            )
            # Always persist immediately
            st.session_state.responses[persist_key] = new_val
            save_data()

            if new_val.strip():
                wc = len(new_val.split())
                st.caption(f"✅ {wc} words pasted")
            else:
                st.caption("⬆️ Not yet pasted")

    st.divider()
    filled = sum(
        1 for m in MODELS
        if st.session_state.responses.get(f"resp_{use_case_name}_{m}", "").strip()
    )
    st.progress(filled / 4, text=f"{filled} / 4 responses entered")
    if filled == 4:
        st.success("All responses ready — go to Step 3 to score them.")

# ======================================================
# TAB 3: SCORING
# ======================================================
with tab3:
    st.subheader("Score each response")
    st.info(
        "**How to score:** Read each model's response on the left, "
        "then rate it 1–5 per criterion on the right using the rubric as your guide. "
        "Add a short qualitative note — you can copy it directly into your paper."
    )

    criteria_list = list(uc["criteria"].keys())

    for model in MODELS:
        color = MODEL_COLORS[model]
        resp_text = st.session_state.responses.get(
            f"resp_{use_case_name}_{model}", ""
        ).strip()

        with st.expander(f"🤖 {model}", expanded=True):
            col_resp, col_scores = st.columns([1, 1], gap="large")

            # ---- LEFT: Response ----
            with col_resp:
                st.markdown("<div class='section-header'>Response</div>", unsafe_allow_html=True)
                if resp_text:
                    safe = (
                        resp_text
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )
                    st.markdown(
                        f"<div class='response-card' style='border-top: 3px solid {color};'>"
                        f"{safe}</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"{len(resp_text.split())} words")
                else:
                    st.warning("No response pasted yet — go to Step 2 first.")

            # ---- RIGHT: Scoring ----
            with col_scores:
                st.markdown("<div class='section-header'>Scores (1 – 5)</div>", unsafe_allow_html=True)
                model_scores = {}

                for crit in criteria_list:
                    crit_desc = uc["criteria"][crit]
                    score_key = f"{use_case_name}_{model}_{crit}"
                    saved_score = st.session_state.scores.get(score_key, 3)

                    st.markdown(
                        f"<div class='rubric-box'>"
                        f"<strong>{crit}</strong><br>"
                        f"<span style='font-size:12px; opacity:0.75;'>{crit_desc}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    score = st.select_slider(
                        label=crit,
                        options=[1, 2, 3, 4, 5],
                        value=saved_score,
                        format_func=lambda x: f"{x} — {SCORE_RUBRIC[x].split('—')[1].strip()}",
                        key=f"slider_{use_case_name}_{model}_{crit}",
                        label_visibility="collapsed"
                    )
                    st.session_state.scores[score_key] = score
                    save_data()
                    model_scores[crit] = score  # always set after slider interaction

                # Average badge
                # Compute average from session_state (same as Step 4) to stay consistent
                ss_vals = [
                    st.session_state.scores[f"{use_case_name}_{model}_{c}"]
                    for c in criteria_list
                    if f"{use_case_name}_{model}_{c}" in st.session_state.scores
                ]
                if ss_vals:
                    avg = sum(ss_vals) / len(ss_vals)
                    if avg >= 4:
                        chip_color = "#28a745"
                    elif avg >= 3:
                        chip_color = "#ffc107"
                    else:
                        chip_color = "#dc3545"
                    st.markdown(
                        f"<div style='margin-top:14px; text-align:right;'>"
                        f"<span class='score-chip' style='"
                        f"background:{chip_color}22; color:{chip_color}; "
                        f"border:1px solid {chip_color}88; font-size:14px; padding:6px 18px;'>"
                        f"Average: {avg:.2f} / 5</span></div>",
                        unsafe_allow_html=True
                    )

                # Qualitative note
                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                note_key = f"{use_case_name}_{model}_note"
                note = st.text_area(
                    "Qualitative observation (optional)",
                    value=st.session_state.notes.get(note_key, ""),
                    height=68,
                    placeholder="e.g. 'Fluent but introduced an unsupported refund guarantee'",
                    key=f"note_{use_case_name}_{model}"
                )
                st.session_state.notes[note_key] = note
                save_data()

        st.divider()

# ======================================================
# TAB 4: RESULTS & EXPORT
# ======================================================
with tab4:
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
        # ---- Helper functions ----
        def get_score(uc_n, model, crit):
            return all_scores_flat.get(f"{uc_n}_{model}_{crit}", None)

        def get_avg(uc_n, model):
            vals = [
                get_score(uc_n, model, c)
                for c in USE_CASES[uc_n]["criteria"]
                if get_score(uc_n, model, c) is not None
            ]
            return round(sum(vals) / len(vals), 2) if vals else None

        def get_overall(model):
            vals = []
            for uc_n, uc_d in USE_CASES.items():
                for c in uc_d["criteria"]:
                    s = get_score(uc_n, model, c)
                    if s is not None:
                        vals.append(s)
            return round(sum(vals) / len(vals), 2) if vals else None

        # ---- Overall Rankings ----
        st.subheader("🏆 Overall Rankings")
        overall_avgs = {m: get_overall(m) for m in MODELS}
        ranked = sorted(
            [(m, v) for m, v in overall_avgs.items() if v is not None],
            key=lambda x: x[1], reverse=True
        )
        rank_labels = ["🥇 1st", "🥈 2nd", "🥉 3rd", "4️⃣ 4th"]

        cols = st.columns(len(ranked))
        for i, (model, avg) in enumerate(ranked):
            color = MODEL_COLORS[model]
            with cols[i]:
                st.markdown(
                    f"<div class='metric-card' style='border-top: 4px solid {color};'>"
                    f"<div style='font-size:13px; opacity:0.6; margin-bottom:4px;'>{rank_labels[i]}</div>"
                    f"<div style='font-size:20px; font-weight:700; color:{color};'>{model}</div>"
                    f"<div style='font-size:34px; font-weight:800; margin:6px 0;'>{avg:.2f}</div>"
                    f"<div style='font-size:12px; opacity:0.55;'>overall avg / 5</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.divider()

        # ---- Radar + Bar ----
        col_radar, col_bar = st.columns(2)

        with col_radar:
            st.subheader("📡 Radar — performance by use case")
            uc_labels = list(USE_CASES.keys())
            short_labels = [u.replace(" ", "\n") for u in uc_labels]
            fig_radar = go.Figure()
            for model in MODELS:
                vals = [get_avg(uc_n, model) or 0 for uc_n in uc_labels]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=short_labels + [short_labels[0]],
                    fill="toself",
                    name=model,
                    line_color=MODEL_COLORS[model],
                    fillcolor=MODEL_COLORS[model],
                    opacity=0.18
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10))),
                showlegend=True,
                height=380,
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(font=dict(size=12))
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_bar:
            st.subheader("📊 Overall average score")
            sorted_models = [m for m, _ in ranked]
            fig_bar = go.Figure(go.Bar(
                x=sorted_models,
                y=[overall_avgs.get(m) or 0 for m in sorted_models],
                marker_color=[MODEL_COLORS[m] for m in sorted_models],
                text=[f"{overall_avgs.get(m):.2f}" if overall_avgs.get(m) else "—" for m in sorted_models],
                textposition="outside",
                width=0.45
            ))
            fig_bar.update_layout(
                yaxis=dict(range=[0, 5.8], title="Score (out of 5)"),
                xaxis_title="",
                height=380,
                showlegend=False,
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ---- Per use case breakdown ----
        st.subheader("🔍 Breakdown by use case and criterion")

        for uc_n, uc_d in USE_CASES.items():
            crit_keys = list(uc_d["criteria"].keys())
            has_uc = any(get_score(uc_n, m, c) is not None for m in MODELS for c in crit_keys)
            if not has_uc:
                continue

            with st.expander(f"📁 {uc_n}", expanded=True):
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
                        if val is None:
                            return ""
                        if val >= 4:
                            return "background-color:#d4edda; color:#155724"
                        if val >= 3:
                            return "background-color:#fff3cd; color:#856404"
                        return "background-color:#f8d7da; color:#721c24"

                    styled = (
                        df.set_index("Criterion")
                        .style
                        .map(color_score, subset=MODELS)
                        .format("{:.0f}", na_rep="—")
                    )
                    st.dataframe(styled, use_container_width=True, height=len(crit_keys) * 38 + 42)

                    uc_avgs = {m: get_avg(uc_n, m) for m in MODELS}
                    valid = {m: v for m, v in uc_avgs.items() if v is not None}
                    if valid:
                        winner = max(valid, key=lambda m: valid[m])
                        st.success(f"**Best:** {winner} ({valid[winner]:.2f}/5)")

                with col_chart:
                    df_melt = df.melt(
                        id_vars="Criterion", var_name="Model", value_name="Score"
                    ).dropna()
                    fig_uc = px.bar(
                        df_melt, x="Criterion", y="Score", color="Model",
                        barmode="group",
                        color_discrete_map=MODEL_COLORS,
                        text_auto=True
                    )
                    fig_uc.update_layout(
                        yaxis=dict(range=[0, 5.8], title="Score (1–5)"),
                        xaxis_title="",
                        height=310,
                        margin=dict(t=10, b=10),
                        xaxis_tickangle=-20,
                        legend=dict(font=dict(size=11))
                    )
                    st.plotly_chart(fig_uc, use_container_width=True)

                notes_for_uc = {
                    m: st.session_state.notes.get(f"{uc_n}_{m}_note", "")
                    for m in MODELS
                }
                if any(v.strip() for v in notes_for_uc.values()):
                    st.markdown("**Qualitative observations:**")
                    for m, note in notes_for_uc.items():
                        if note.strip():
                            st.markdown(
                                f"<span style='color:{MODEL_COLORS[m]}; font-weight:600;'>"
                                f"{m}:</span> {note}",
                                unsafe_allow_html=True
                            )

        st.divider()

        # ---- Heatmap ----
        st.subheader("🌡️ Full criteria heatmap")
        heat_z, heat_text, y_labels = [], [], []
        for uc_n, uc_d in USE_CASES.items():
            for c in uc_d["criteria"]:
                row = [get_score(uc_n, m, c) for m in MODELS]
                heat_z.append(row)
                heat_text.append([str(v) if v is not None else "—" for v in row])
                short_uc = uc_n[:16] + ("…" if len(uc_n) > 16 else "")
                y_labels.append(f"{short_uc} | {c}")

        fig_heat = go.Figure(go.Heatmap(
            z=heat_z,
            x=MODELS,
            y=y_labels,
            colorscale=[
                [0.0,  "#f8d7da"],
                [0.25, "#fd7e14"],
                [0.5,  "#fff3cd"],
                [0.75, "#8bc34a"],
                [1.0,  "#d4edda"]
            ],
            zmin=1, zmax=5,
            text=heat_text,
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Score", tickvals=[1, 2, 3, 4, 5])
        ))
        fig_heat.update_layout(
            height=max(340, len(heat_z) * 32 + 60),
            margin=dict(l=230, t=30, b=20, r=20),
            xaxis=dict(side="top")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()

        # ---- Export ----
        st.subheader("📄 Export for your paper")

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            st.markdown("**Full scores (all criteria)**")
            export_rows = []
            for uc_n, uc_d in USE_CASES.items():
                for c in uc_d["criteria"]:
                    row = {"Use Case": uc_n, "Criterion": c}
                    for m in MODELS:
                        row[m] = get_score(uc_n, m, c) or ""
                    export_rows.append(row)
            export_df = pd.DataFrame(export_rows)
            st.dataframe(export_df, use_container_width=True)
            st.download_button(
                "⬇️ Download full CSV",
                export_df.to_csv(index=False).encode("utf-8"),
                "llm_benchmark_full.csv", "text/csv"
            )

        with col_e2:
            st.markdown("**Summary table (avg per use case)**")
            summary_rows = []
            for uc_n in USE_CASES:
                row = {"Use Case": uc_n}
                for m in MODELS:
                    v = get_avg(uc_n, m)
                    row[m] = f"{v:.2f}" if v else "—"
                summary_rows.append(row)
            summary_df = pd.DataFrame(summary_rows)
            st.dataframe(summary_df, use_container_width=True)
            st.download_button(
                "⬇️ Download summary CSV",
                summary_df.to_csv(index=False).encode("utf-8"),
                "llm_benchmark_summary.csv", "text/csv"
            )

        # Qualitative notes
        all_notes = {
            f"{uc_n} / {m}": st.session_state.notes.get(f"{uc_n}_{m}_note", "")
            for uc_n in USE_CASES
            for m in MODELS
        }
        if any(v.strip() for v in all_notes.values()):
            st.divider()
            st.markdown("**Qualitative observations (paste into your discussion section):**")
            for label, note in all_notes.items():
                if note.strip():
                    st.markdown(f"- **{label}:** {note}")

# ======================================================
# TAB 5: HALLUCINATION LEADERBOARD
# ======================================================
with tab5:

    # ---- CSS for leaderboard ----
    st.markdown("""
    <style>
    .lb-header {
        text-align: center;
        padding: 28px 0 8px 0;
    }
    .lb-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .lb-subtitle {
        font-size: 13px;
        opacity: 0.55;
        margin-bottom: 0;
    }
    .lb-row {
        display: flex;
        align-items: center;
        padding: 14px 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 10px;
        gap: 16px;
    }
    .lb-rank {
        font-size: 22px;
        font-weight: 800;
        min-width: 36px;
        text-align: center;
    }
    .lb-model {
        font-size: 17px;
        font-weight: 700;
        min-width: 100px;
    }
    .lb-bar-wrap {
        flex: 1;
        background: rgba(128,128,128,0.1);
        border-radius: 99px;
        height: 12px;
        overflow: hidden;
    }
    .lb-bar-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.6s ease;
    }
    .lb-score {
        font-size: 20px;
        font-weight: 800;
        min-width: 52px;
        text-align: right;
    }
    .lb-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 99px;
        min-width: 90px;
        text-align: center;
    }
    .lb-detail {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 6px;
    }
    .lb-pill {
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 99px;
        opacity: 0.8;
    }
    .lb-divider {
        border: none;
        border-top: 1px solid rgba(128,128,128,0.12);
        margin: 20px 0;
    }
    .stat-box {
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .stat-val { font-size: 22px; font-weight: 800; }
    .stat-lbl { font-size: 11px; opacity: 0.55; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

    # ---- Collect hallucination scores ----
    hall_data = {}
    for uc_n, uc_d in USE_CASES.items():
        matched = next((k for k in uc_d["criteria"] if "hallucin" in k.lower()), None)
        if not matched:
            continue
        hall_data[uc_n] = {}
        for m in MODELS:
            val = st.session_state.scores.get(f"{uc_n}_{m}_{matched}")
            hall_data[uc_n][m] = val

    uc_names = [u for u in hall_data if any(v is not None for v in hall_data[u].values())]
    has_hall = bool(uc_names)

    if not has_hall:
        st.info("No hallucination scores yet — complete Step 3 first.")
    else:
        import pandas as pd

        # Compute per-model averages
        model_avgs = {}
        for m in MODELS:
            vals = [hall_data[uc_n][m] for uc_n in uc_names if hall_data[uc_n].get(m) is not None]
            model_avgs[m] = round(sum(vals) / len(vals), 2) if vals else None

        ranked = sorted(
            [(m, v) for m, v in model_avgs.items() if v is not None],
            key=lambda x: x[1], reverse=True
        )

        def risk_label(score):
            if score >= 4.5: return ("🟢 Excellent", "#1a9e5c", "#e6f9f0")
            if score >= 4.0: return ("🟢 Low risk",  "#1a9e5c", "#e6f9f0")
            if score >= 3.0: return ("🟡 Moderate",  "#b8860b", "#fdf8e1")
            return              ("🔴 High risk",  "#c0392b", "#fdecea")

        rank_icons = ["🥇", "🥈", "🥉", "4️⃣"]

        # ---- Header ----
        st.markdown("""
        <div class="lb-header">
            <div class="lb-title">🧠 Hallucination Leaderboard</div>
            <div class="lb-subtitle">
                Ranked by Hallucination Avoidance score (1–5) · Higher = more reliable · Lower = more prone to fabrication
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='lb-divider'>", unsafe_allow_html=True)

        # ---- Leaderboard rows ----
        for i, (model, avg) in enumerate(ranked):
            color = MODEL_COLORS[model]
            bar_pct = int((avg / 5) * 100)
            risk_text, risk_color, risk_bg = risk_label(avg)
            risk_score = round(6 - avg, 2)

            # Per-use-case pills
            pills_html = ""
            for uc_n in uc_names:
                v = hall_data[uc_n].get(model)
                if v is not None:
                    short = uc_n.split()[0]
                    pill_color = "#1a9e5c" if v >= 4 else "#b8860b" if v >= 3 else "#c0392b"
                    pills_html += (
                        f"<span class='lb-pill' style='background:{pill_color}18; "
                        f"color:{pill_color}; border:1px solid {pill_color}44;'>"
                        f"{short}: {v}/5</span>"
                    )

            st.markdown(f"""
            <div class="lb-row" style="border-left: 5px solid {color};">
                <div class="lb-rank">{rank_icons[i]}</div>
                <div style="flex:0 0 110px;">
                    <div class="lb-model" style="color:{color};">{model}</div>
                    <div class="lb-detail">{pills_html}</div>
                </div>
                <div class="lb-bar-wrap">
                    <div class="lb-bar-fill" style="width:{bar_pct}%; background:{color};"></div>
                </div>
                <div class="lb-score" style="color:{color};">{avg:.2f}<span style="font-size:12px; font-weight:400; opacity:0.5;">/5</span></div>
                <div class="lb-badge" style="background:{risk_bg}; color:{risk_color}; border:1px solid {risk_color}44;">
                    {risk_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='lb-divider'>", unsafe_allow_html=True)

        # ---- Summary stats row ----
        st.markdown("#### 📊 Summary statistics")
        all_vals = [v for m, v in model_avgs.items() if v is not None]
        best_model, best_score = ranked[0]
        worst_model, worst_score = ranked[-1]
        gap = round(best_score - worst_score, 2)
        avg_all = round(sum(all_vals) / len(all_vals), 2)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-val" style="color:{MODEL_COLORS[best_model]};">{best_model}</div>
                <div class="stat-lbl">Most reliable model</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-val" style="color:{MODEL_COLORS[worst_model]};">{worst_model}</div>
                <div class="stat-lbl">Most prone to hallucination</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-val">{avg_all:.2f}</div>
                <div class="stat-lbl">Group average / 5</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-val">{gap}</div>
                <div class="stat-lbl">Score gap (best vs worst)</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='lb-divider'>", unsafe_allow_html=True)

        # ---- Chart: avoidance vs risk side by side ----
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### Avoidance score by use case")
            bar_rows = []
            for uc_n in uc_names:
                for m in MODELS:
                    v = hall_data[uc_n].get(m)
                    if v is not None:
                        bar_rows.append({"Use Case": uc_n, "Model": m, "Score": v})
            if bar_rows:
                df_b = pd.DataFrame(bar_rows)
                fig_b = go.Figure()
                for m in MODELS:
                    s = df_b[df_b["Model"] == m]
                    fig_b.add_trace(go.Bar(
                        name=m, x=s["Use Case"], y=s["Score"],
                        marker_color=MODEL_COLORS[m],
                        text=s["Score"], textposition="outside"
                    ))
                fig_b.update_layout(
                    barmode="group",
                    yaxis=dict(range=[0, 5.8], title="Score (1–5, higher = better)"),
                    xaxis_title="", height=320,
                    margin=dict(t=10, b=10),
                    legend=dict(font=dict(size=11))
                )
                st.plotly_chart(fig_b, use_container_width=True)

        with col_r:
            st.markdown("#### Hallucination risk score by use case")
            st.caption("Inverted: higher = more prone to hallucination")
            if bar_rows:
                df_r = pd.DataFrame(bar_rows)
                df_r["Risk"] = 6 - df_r["Score"]
                fig_r = go.Figure()
                for m in MODELS:
                    s = df_r[df_r["Model"] == m]
                    fig_r.add_trace(go.Bar(
                        name=m, x=s["Use Case"], y=s["Risk"],
                        marker_color=MODEL_COLORS[m],
                        text=s["Risk"].round(1), textposition="outside"
                    ))
                fig_r.update_layout(
                    barmode="group",
                    yaxis=dict(range=[0, 5.8], title="Risk (higher = worse)"),
                    xaxis_title="", height=320,
                    margin=dict(t=10, b=10),
                    legend=dict(font=dict(size=11))
                )
                st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("<hr class='lb-divider'>", unsafe_allow_html=True)

        # ---- Detailed score table ----
        st.markdown("#### Detailed scores")
        table_rows = []
        for uc_n in uc_names:
            for m in MODELS:
                v = hall_data[uc_n].get(m)
                if v is None:
                    continue
                risk_t, _, _ = risk_label(v)
                table_rows.append({
                    "Use Case": uc_n, "Model": m,
                    "Avoidance Score": v,
                    "Risk Score": round(6 - v, 1),
                    "Risk Level": risk_t
                })
        if table_rows:
            df_tbl = pd.DataFrame(table_rows)
            def color_avoidance(val):
                if isinstance(val, (int, float)):
                    if val >= 4: return "background-color:#d4edda; color:#155724"
                    if val >= 3: return "background-color:#fff3cd; color:#856404"
                    return "background-color:#f8d7da; color:#721c24"
                return ""
            styled_tbl = (
                df_tbl.style
                .map(color_avoidance, subset=["Avoidance Score", "Risk Score"])
            )
            st.dataframe(styled_tbl, use_container_width=True, hide_index=True)


st.divider()
st.caption(
    "LLM Benchmarking Dashboard · Firdaouss El Mouden · "
    "Justus-Liebig-Universität Gießen · No API key required"
)
