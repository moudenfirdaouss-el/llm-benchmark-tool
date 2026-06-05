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
st.markdown("ffffff;
        min-height: 200px;
        font-size: 13px;
        line-height: 1.6;
        color: #1a1a1a;
    }
    .section-header-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
for key in ["scores", "responses", "notes"]:
    if key not in st.session_state:
        st.session_state[key] = {}

MODELS = ["Claude", "ChatGPT", "Gemini"]or gaps",
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
2. Paste all 3 LLM responses (Step 2)
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
st.caption(f"HELM-inspired evaluation · {use_case_name} · Claude · ChatGPT · Gemini")

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
    st.info("Copy this exact prompt and run it in **Claude.ai**, **ChatGPT**, and **Gemini**. Then paste each response in Step 2.")

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
    st.subheader("Paste the three LLM responses")
    st.caption("Paste each model's exact response to the prompt above. You can save and come back — responses are kept in memory during your session.")

    cols = st.columns(3)
    for i, model in enumerate(MODELS):
        with cols[i % 3]:
            color = MODEL_COLORS[model]
            st.markdown(f"<p style='color:{color}; font-weight:700_case_name}_{model}"
            val = st.session_state.responses.get(persist_key, "")
            new_val = st.text_area(
                f"{model} response",
                value=val,
                height=220,
                placeholder=f"Paste {model}'s response here...",
                key=f"ta_{use_case_name}_{model}",
                label_visibility="collapsed"
            )
            st.session_state.responses[persist_key] = new_val
            if new_val.strip():
                wc = len(new_val.split())
                st.caption(f"✅ {wc} words")
            else:
                st.caption("⬆️ Not yet pasted")

    st.divider()
    filled = sum(1 for m in MODELS if st.session_state.responses.get(f"resp_{use_case_name}_{m}", "").strip())
    st.progress(filled / 3, text=f"{filled}/3 responses entered — go to Step 3 to score them")

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
        resp_text = st.session_state.responses.get(f"resp_{use_case_name}_{model}", "").strip()

        with st.expander(f"🤖 {model}", expanded=True):
            col_resp, col_scores = st.columns([1, 1])

            with col_resp:
                st.markdown("<div class='section-header'>Response</div>", unsafe_allow_html=True)
                if resp_text:
                    st.markdown(f"""
                    <div class="response-card" style="border) > 1800 else ''}
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

                    score = st.CORE_RUBRIC[x].split('—')[1].strip()}",
                        key=f"slider_{use_case_name}_{model}_{crit}",
                        label_visibility="collapsed"
                    )
                    st.session_state.scores[score_key] = score
                    model_scores[crit] = score

                if model_scores:
                    avg = sum(model_scores.values()) / len(model_scores)
                    chip_color = "#28a745" if avg >= 4 else "#ffc107" if avg >= 3 else "#dc3545"
                    stcolor}; border:1px solid {chip_color}66; font-size:14px; padding:5px 16px;">
                            Average: {avg:.2f} / 5
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

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

        st.subhe```
