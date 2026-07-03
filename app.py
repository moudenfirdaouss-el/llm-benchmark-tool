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
        "scores":         dict(st.session_state.scores),
        "responses":      dict(st.session_state.responses),
        "notes":          dict(st.session_state.notes),
        "elo":            dict(st.session_state.elo),
        "votes": dict(st.session_state.votes),
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============ SESSION STATE ============
if "scores" not in st.session_state:
    _saved = load_data()
    st.session_state.scores         = _saved["scores"]
    st.session_state.responses      = _saved["responses"]
    st.session_state.notes          = _saved["notes"]
    st.session_state.elo            = _saved.get("elo", {})
    st.session_state.votes = _saved.get("votes", {})

# Always ensure elo and votes exist (survive reruns)
if "elo" not in st.session_state:
    st.session_state.elo = {}
if "votes" not in st.session_state:
    st.session_state.votes = {}

# ============ PRE-LOAD FINANCIAL USE CASE DATA ============
_FINANCIAL_UC = "Financial Statement Analysis"
_FINANCIAL_RESPONSES = {
    "Claude": """# Merck KGaA – Q1 2026 Financial Analysis

1. Key Financial Risks

Revenue Contraction
Group net sales declined 2.8% YoY to €5,133.7M in Q1 2026. The decline is broad-based, with Healthcare down 3.0% and Electronics down 13.9%, partially offset by Life Science growth of 2.2%.

Persistent FX Headwinds
Foreign exchange translation remains a significant drag across all segments. At the Group level, FX represented a -€287.8M / -5.4% headwind in Q1 2026 YoY. All three operating divisions show material FX-driven revenue erosion, indicating structural exposure to currency volatility.

Healthcare Margin Compression
Healthcare EBITDA pre margin contracted sharply to 35.0% in Q1 2026 from 37.6% in Q1 2025 (-270 bps). EBIT declined 23.7% YoY to €536.3M. Depreciation and amortization surged 56.2% YoY, largely driven by a >1,000% increase in intangible asset amortization within cost of sales — consistent with the amortization profile of a recent acquisition (evidenced by €93.4M in acquisition-related revenue in Q1 2026).

Rising Leverage
Net financial debt stands at €8,318.5M as of 31 March 2026, with a Net Debt / EBITDA pre ratio of 1.4x. While within manageable bounds, this is elevated relative to the 1.2x recorded at end of Q1 2025, reflecting the significant acquisition-driven debt increase in 2025 (FY investing cash outflow of -€4,261.2M).

Elevated Restructuring and Integration Costs
Total adjustments in Q1 2026 reached €96.0M, up 71.4% YoY. Integration costs alone grew 266.6% YoY to €62.2M, indicating ongoing operational disruption from recent M&A activity.

Profitability Deterioration
Group EBIT declined 6.8% YoY to €937.2M. Profit before tax fell 9.1% and profit after tax declined 9.4% to €668.8M. EPS (reported) declined 10.1% YoY to €1.52.

2. Growth Opportunities

Life Science Organic Momentum
Life Science delivered organic revenue growth of 8.3% in Q1 2026 (€183.1M organic delta), the strongest organic performance across all segments. EBITDA pre grew 4.2% YoY to €648.6M, with margins broadly stable at 28.6%. This represents a resilient core business with accelerating organic demand.

Electronics Recovery
Electronics posted organic growth of €40.2M in Q1 2026, a meaningful improvement following a period of contraction. EBITDA pre surged 15.5% YoY to €282.2M, and the EBITDA pre margin expanded substantially to 34.6% from 25.8% in Q1 2025 — the strongest margin in the segment for the periods disclosed. EBIT rose 69.1% YoY to €163.3M. This suggests a cyclical recovery may be underway.

Strong Operating Cash Generation
Operating cash flow grew 47.2% YoY to €818.0M in Q1 2026, despite revenue headwinds. This indicates improving cash conversion and supports the capacity to service debt and fund continued investment.

Healthcare Acquisition Integration
The acquisition absorbed in 2025 (reflected in €93.4M of acquisition-related revenue in Healthcare Q1 2026) has yet to generate full margin contribution, as integration costs remain elevated. If successfully integrated, it presents a meaningful medium-term earnings accretion opportunity.

Improving Cash Position
Cash and cash equivalents grew 173.0% YoY to €2,743.1M as of 31 March 2026, providing significant liquidity optionality.

3. Overall Company Outlook

Merck KGaA enters Q1 2026 in a transitional phase. The Group's reported financials reflect near-term pressure from three converging factors: FX headwinds, post-acquisition amortization drag in Healthcare, and elevated integration expenditure. These weigh on reported profitability metrics, though the adjusted EBITDA pre (-0.3% YoY, €1,530.1M) suggests the underlying operating business is substantially more stable than headline earnings imply.

The divergence between reported EPS (-10.1%) and EPS pre (-0.5%) is material and signals that the earnings decline is largely driven by non-recurring and acquisition-related items rather than fundamental business deterioration.

Life Science provides a stable, growing foundation. Electronics shows early signs of a recovery cycle. Healthcare's short-term pressure is structural (amortization, integration) rather than demand-driven, given that organic revenue was still negative (-€71.8M), warranting close monitoring.

Key metrics to watch: organic revenue trajectory in Healthcare, Electronics margin sustainability, debt reduction pace, and normalisation of integration costs.

All figures sourced directly from the Merck KGaA Q1 2026 Financial Statements. Interpretations are clearly indicated and based solely on disclosed data.""",

    "ChatGPT": """## 1. Key Financial Risks

Foreign exchange headwinds:
The report shows a significant negative currency impact across all business sectors. Group net sales were negatively affected by €287.8 million from FX effects in Q1 2026. EBITDA pre was also negatively impacted by €87.4 million due to currency movements.

Declining Healthcare sales and earnings:
Healthcare net sales declined 3.0% year-over-year in Q1 2026, while Healthcare EBIT fell 23.7%. This indicates pressure on profitability in one of the company's major divisions.

Rising research and development expenses:
Group R&D costs increased 19.3% year-over-year to €657.7 million in Q1 2026, representing 12.8% of net sales. Healthcare R&D expenses increased 28.1% year-over-year. While strategically important, elevated R&D spending may pressure margins in the near term.

High adjustment and integration costs:
Integration and IT-related costs rose sharply, increasing 266.6% year-over-year to €62.2 million in Q1 2026. Total adjustments increased 71.4% year-over-year. This suggests ongoing restructuring and integration-related financial burden.

Pressure in Electronics segment:
Electronics net sales declined 7.1% year-over-year in FY 2025 and remained weak in Q1 2026, with Q1 sales down by €131.6 million year-over-year. EBITDA pre in Electronics had previously declined materially, highlighting earnings volatility in the segment.

## 2. Growth Opportunities

Organic growth across core businesses:
Despite currency headwinds, Group organic sales growth was positive at 3.1% in Q1 2026. Life Science achieved 4.0% organic growth in FY 2025 and continued growth into Q1 2026.

Strong profitability in Life Science:
Life Science EBITDA pre increased 4.2% year-over-year to €648.6 million in Q1 2026. EBIT margin improved to 17.8% from 16.6% in the prior-year quarter. This suggests operational resilience and margin improvement potential.

Improved Group profitability margin:
Group EBITDA pre margin increased to 29.8% in Q1 2026 from 29.1% in Q1 2025. This reflects stable operational performance despite lower sales.

Positive organic EBITDA growth:
Group EBITDA pre organic growth was 5.7% in Q1 2026. This indicates underlying operational strength excluding FX and acquisition effects.

## 3. Overall Company Outlook

Merck KGaA reported resilient operational performance in Q1 2026 despite lower reported sales and substantial foreign exchange headwinds. Group net sales declined 2.8% year-over-year to €5.1 billion, while EBITDA pre remained broadly stable at €1.53 billion.

The company's outlook appears supported by continued positive organic growth, stable EBITDA pre margins, and strong performance in Life Science. However, the report also indicates ongoing challenges from FX volatility, declining Healthcare profitability, elevated restructuring and integration costs, and continued pressure in Electronics.

Overall, the financial report supports a view of stable underlying operational performance with mixed segment dynamics and continued cost and currency-related pressures.""",

    "Gemini": """Based on the quantitative and qualitative indicators contained within the Q1 2026 financial report of Merck KGaA, the structured summary is as follows:

1. Key Financial Risks

Foreign Exchange (Fx) Headwinds: Adverse foreign exchange impacts significantly constrained performance across all segments. On a Group level, foreign currency fluctuations reduced net sales by €287.8 million and EBITDA pre by €87.4 million during Q1 2026.

Increasing Costs: The Group experienced rising expenses across multiple layers of the profit and loss statement, including a 3.1% YoY increase in the Cost of Sales (€2,068.8 million), a 13.4% rise in Administration expenses (€402.7 million), and a notable 19.3% expansion in Research and Development (R&D) costs (€657.7 million).

Escalating Restructuring and IT/Integration Outlays: Restructuring costs increased by 25.5% YoY to €30.0 million. Simultaneously, IT and Integration costs jumped by 266.6% YoY to €62.2 million.

Contraction in Core Profitability Metrics: Total EBIT decreased by 6.8% YoY to €937.2 million, while Profit After Tax contracted by 9.4% to €668.8 million. Earnings Per Share (EPS) declined by 10.1% YoY to €1.52.

Organic Declines in Healthcare: While other business sectors posted organic expansions, the Healthcare sector reported negative organic sales growth of -€71.8 million and an organic decline in EBITDA pre of -€14.2 million.

2. Growth Opportunities

Organic Performance in Life Science and Electronics: In Q1 2026, Life Science achieved positive organic sales growth of €183.1 million and organic EBITDA pre growth of €45.8 million. Electronics demonstrated an organic expansion of €40.2 million in sales and €73.5 million in EBITDA pre.

Acquisition-Driven Expansion in Healthcare: Despite organic pullbacks, the Healthcare division generated substantial top-line gains via portfolio additions, securing €93.4 million in net sales from acquisitions and adding €4.4 million to its EBITDA pre.

Electronics Profit Margin Optimization: The Electronics business sector expanded its financial performance margins considerably, with its Q1 2026 EBITDA pre margin climbing to 34.6% — up from 23.7% for the full financial year 2025.

3. Overall Company Outlook

Stable Consolidated Net Sales with Underlying Organic Health: On a reported YoY basis, consolidated Group net sales felt slight downward pressure, moving from €5,280.1 million in Q1 2025 to €5,133.7 million in Q1 2026. However, underlying organic baseline adjustments reveal robust core performance, yielding an overall positive organic volume growth of €151.5 million across the Group.

Resilient Non-GAAP Operating Profitability: Despite high operational spending and macroeconomic currency challenges, the Group demonstrated solid operational stability. Consolidated EBITDA pre softened by only an incremental -0.3% YoY to €1,530.1 million (compared to €1,535.1 million in Q1 2025). This resulted in an expanded overall Group EBITDA pre margin of 29.8%, compared to 29.1% in the prior year's opening quarter.""",

    "Deepseek": """Based solely on the provided financial report for Merck KGaA (Q1 2025 – Q1 2026), here is the requested analysis.

1. Top 3 Key Financial Risks

Risk 1: Declining Net Sales in Q1 2026 vs. Q1 2025
Observed fact: Group net sales decreased from €5,280.1 million (Q1 2025) to €5,133.7 million (Q1 2026).
Specific figure: YoY change of -€146.5 million (or -2.8% as shown in the Change YoY column on Page 3).
Inferred conclusion: The company is facing top-line contraction entering 2026, which could pressure profitability if not reversed.

Risk 2: Sharp Contraction in Healthcare Segment EBITDA pre
Observed fact: Healthcare EBITDA pre (a key profit metric) fell from €795.8 million (Q1 2025) to €718.3 million (Q1 2026).
Specific figure: YoY change of -€77.5 million (Page 2, bottom section).
Inferred conclusion: This represents a nearly 10% decline in core operating profitability in the largest segment by margin, signaling possible pricing pressure, cost inflation, or reduced demand.

Risk 3: Negative Operating Cash Flow from Working Capital Changes
Observed fact: Changes in working capital were -€322.4 million in Q1 2026 (Page 15).
Specific figure: Within this, trade accounts receivable worsened by -€262.5 million (YoY change -11.6%), and inventories consumed -€144.4 million (YoY change +26.7%).
Inferred conclusion: The company is tying up more cash in receivables and inventory, which may indicate slower collection cycles or overstocking – a liquidity risk if sustained.

2. Main Growth Opportunities

Opportunity 1: Electronics Segment Margin Expansion
Observed fact: Electronics EBITDA pre margin increased sharply from 25.8% (Q1 2025) to 34.6% (Q1 2026).
Specific figure: EBITDA pre in Electronics rose by €37.9 million YoY, from €244.3 million to €282.2 million (Page 2).
Inferred conclusion: Despite flat or declining sales in some quarters, the segment is becoming significantly more profitable, suggesting operational leverage, cost control, or a shift to higher-margin products.

Opportunity 2: Strong Organic Growth in Life Science
Observed fact: Life Science organic sales growth (excluding currency and acquisition effects) was +€45.8 million in Q1 2026 vs. Q1 2025.
Specific figure: Organic Delta = +€45.8 million (Page 2, Life Science row).
Inferred conclusion: The core Life Science business continues to grow on a like-for-like basis, indicating resilient demand for its products/services.

Opportunity 3: Cash Flow Improvement from Operations
Observed fact: Operating cash flow increased from €555.8 million (Q1 2025) to €818.0 million (Q1 2026).
Specific figure: YoY change of +47.2% (Page 15).
Inferred conclusion: Despite lower net sales, the company is generating substantially more cash from operations, which could be deployed for debt reduction, R&D, or acquisitions.

3. Overall Company Outlook Assessment

Assessment: NEUTRAL

Negative signals: Group net sales declined YoY (-2.8%). Healthcare EBITDA pre fell significantly (-€77.5 million). Working capital absorption increased, especially in receivables and inventory.

Positive signals: Operating cash flow improved strongly (+47.2%). Electronics margin expanded dramatically (+8.8 percentage points). Life Science showed positive organic growth.

Inferred conclusion: The company is not in a clear growth trajectory (declining sales in Q1 2026 vs. Q1 2025), but underlying cash generation and margin improvements in one key segment (Electronics) provide a buffer. The mixed signals across segments and the deterioration in Healthcare suggest caution. Therefore, a neutral outlook is most consistent with the data."""
}

_FINANCIAL_SCORES = {
    "Claude":   {"Factual Accuracy": 5, "Clarity": 4, "Hallucination Avoidance": 5, "Financial Terminology": 5, "Source Grounding": 5, "Analytical Sophistication": 5},
    "ChatGPT":  {"Factual Accuracy": 4, "Clarity": 5, "Hallucination Avoidance": 4, "Financial Terminology": 4, "Source Grounding": 4, "Analytical Sophistication": 4},
    "Gemini":   {"Factual Accuracy": 3, "Clarity": 3, "Hallucination Avoidance": 3, "Financial Terminology": 5, "Source Grounding": 3, "Analytical Sophistication": 4},
    "Deepseek": {"Factual Accuracy": 4, "Clarity": 5, "Hallucination Avoidance": 5, "Financial Terminology": 3, "Source Grounding": 5, "Analytical Sophistication": 4},
}

# Only inject if not already saved by user
_needs_preload = not any(
    k.startswith(_FINANCIAL_UC)
    for k in st.session_state.scores
)
if _needs_preload:
    for _m, _resp in _FINANCIAL_RESPONSES.items():
        st.session_state.responses[f"resp_{_FINANCIAL_UC}_{_m}"] = _resp
    for _m, _sc in _FINANCIAL_SCORES.items():
        for _crit, _val in _sc.items():
            st.session_state.scores[f"{_FINANCIAL_UC}_{_m}_{_crit}"] = _val
    save_data()


_CS_UC = "Customer Service Chatbot"
_CS_RESPONSES = {
    "Claude": """Subject: Re: Your Recent Booking – Duplicate Charge Investigation

Dear Valued Customer,

Thank you for reaching out to us, and please accept our sincere apologies for the frustration this situation has caused. Being charged twice for a booking — and then not receiving a timely resolution — is absolutely not the experience we want for our customers, and we understand your concern completely.

We take billing discrepancies very seriously. To resolve this as quickly as possible, we have escalated your case to our Billing & Payments team, who are authorized to investigate duplicate charges and process refunds directly.

Here is what you can expect next:
• A member of our Billing team will review your account and confirm the duplicate transaction within 2 business days.
• Once confirmed, your refund will be initiated. Please note that depending on your bank or card provider, refunds typically appear within 5–10 business days after processing.
• You will receive an email confirmation as soon as the refund has been issued.

To help us prioritize your case, could you please provide the following details if you haven't already?
  – Your booking reference number
  – The email address used at the time of booking
  – The date(s) the charges appeared on your statement

We genuinely regret that your previous contact did not result in a resolution, and we are committed to making this right. Please do not hesitate to reply to this message directly if you have any further questions — your case is now being handled as a priority.

Thank you for your patience, and we appreciate the opportunity to correct this for you.

Warm regards,
Customer Relations Team""",

    "ChatGPT": """Dear Customer,

Thank you for reaching out, and I sincerely apologize for the frustration and inconvenience this situation has caused.

I understand how concerning it is to see a duplicate charge while still waiting for a resolution after contacting support previously. In some cases, duplicate charges can occur due to payment authorization delays or processing errors between the bank and booking system.

To help resolve this as quickly as possible, I recommend that we review the transaction details immediately. Please reply with the following information:
* Your booking reference number
* The full name on the reservation
* The dates and amounts of both charges
* A screenshot or copy of your bank statement showing the duplicate transaction (with sensitive information hidden)

Once we receive these details, we can escalate the case to our billing team for priority review. If a duplicate payment is confirmed, the refund will be processed according to the payment provider's standard processing timelines.

We truly appreciate your patience and apologize again for the delay in resolving this matter. We are committed to assisting you until the issue is fully addressed.

Kind regards,
Customer Support Team""",

    "Gemini": """Dear Valued Customer,

Thank you for reaching out to us. I am sincerely sorry for the frustration and inconvenience this situation has caused you. Discovering a duplicate charge is stressful enough, and I completely understand how disappointing it is that this was not resolved after your contact last week. This is certainly not the level of service we aim to provide.

I want to help you get this sorted out as quickly as possible.

What Likely Happened:
When a duplicate charge occurs, it is typically due to one of two reasons:
* A Processing Glitch: A temporary technical interruption during checkout can occasionally cause the payment gateway to submit the charge twice.
* An Authorization Hold: Sometimes, the bank places a temporary hold on the funds that looks like a charge, which usually drops off automatically within a few business days.

Next Steps to Resolve This:
Because your previous request was not finalized, I have personally escalated this issue to our billing and finance department for an immediate priority review.

To ensure we resolve this accurately, could you please reply with a few details?
* Your Booking Reference (PNR) or ticket number.
* The date the transactions occurred.
* A screenshot or copy of the bank statement showing the two identical charges.

What to Expect:
Once our finance team verifies the duplicate transaction, we will process the refund immediately. Standard billing procedures mean a refund typically takes 5 to 7 business days to reflect in your account, depending entirely on your financial institution's processing times. I will monitor your case personally and send you a confirmation email with the refund receipt the moment it is approved.

Thank you for your patience and for bringing this to our attention again. We appreciate your business and are committed to making this right.

Warm regards,
Customer Support Team
Flight Excellence Airlines""",

    "Deepseek": """Subject: Apologies for the double charge and delay in resolving your refund

Dear [Customer Name],

Thank you for reaching out, and I'm truly sorry for the frustration and inconvenience this double charge has caused you. I completely understand how upsetting it must be to see an extra charge on your account, especially after waiting a week without a resolution.

Let me explain what may have happened: Sometimes, during the booking process, a temporary authorization is placed on your card — this can appear as a second charge but is typically reversed automatically within a few business days. However, in some cases, a genuine duplicate transaction occurs due to a system error.

I have personally reviewed your booking record using the email address and flight details associated with your complaint. I can confirm that a duplicate charge was indeed applied to your transaction on [date of booking]. The refund for the duplicate amount of [amount] was initiated on [date], but I see that it has not yet reflected in your account — this delay is unacceptable, and I sincerely apologize for that.

What I will do for you right now:
I have escalated your case to our billing department with high priority, reference number REF-XXXXXX. They have confirmed that the refund will be processed within 3 business days directly to your original payment method. You do not need to take any further action.

What you can expect from us:
- You will receive a confirmation email from our billing team within 24 hours.
- If the refund does not appear in your account by [date + 3 business days], please reply to this email and I will personally ensure a manual reversal via our finance team.

I cannot promise an immediate refund solely from this message, as bank processing times vary, but I can promise that your case is now actively tracked and prioritized.

Again, I deeply regret the frustration this has caused and thank you for your patience. We are committed to making this right.

Best regards,
[Your Full Name]
Customer Service Representative
[Airline Name]
[Reference/Contact Info]"""
}

_CS_SCORES = {
    "Claude":   {"Clarity": 5, "Empathy": 5, "Helpfulness": 4, "Professional Tone": 5, "Hallucination Avoidance": 5, "Robustness": 5},
    "ChatGPT":  {"Clarity": 5, "Empathy": 4, "Helpfulness": 4, "Professional Tone": 5, "Hallucination Avoidance": 4, "Robustness": 4},
    "Gemini":   {"Clarity": 4, "Empathy": 5, "Helpfulness": 4, "Professional Tone": 4, "Hallucination Avoidance": 3, "Robustness": 3},
    "Deepseek": {"Clarity": 4, "Empathy": 5, "Helpfulness": 4, "Professional Tone": 4, "Hallucination Avoidance": 2, "Robustness": 3},
}

_needs_cs_preload = not any(k.startswith(_CS_UC) for k in st.session_state.scores)
if _needs_cs_preload:
    for _m, _resp in _CS_RESPONSES.items():
        st.session_state.responses[f"resp_{_CS_UC}_{_m}"] = _resp
    for _m, _sc in _CS_SCORES.items():
        for _crit, _val in _sc.items():
            st.session_state.scores[f"{_CS_UC}_{_m}_{_crit}"] = _val
    save_data()


_HR_UC = "HR Recruitment"
_HR_RESPONSES = {
    "Claude": """## Candidate Ranking for Marketing Manager Position

### Rank 1: Candidate A
Overall fit: Strong match across all core requirements

Candidate A meets or exceeds every listed requirement. With 7 years of marketing experience, they surpass the 5-year threshold, and their leadership of 8-person teams directly satisfies the team management criterion. Their digital marketing skill set — SEO, SEM, and social media — aligns precisely with what the role demands. The MBA adds credibility to their strategic capability, and their extensive B2B SaaS background is a standout given that B2B experience is explicitly preferred.

Development areas: Email marketing is not mentioned, which is a minor gap worth exploring in screening.

### Rank 2: Candidate C
Overall fit: Solid match with some gaps

Candidate C's 6 years of combined marketing and sales experience meets the tenure requirement, and their strong CRM and data analytics background is a genuine differentiator — arguably stronger in this area than Candidate A. Two years of team leadership is a positive, though less extensive than the role may require at a senior level. The mixed sales background could also be an asset in a B2B environment, though no explicit B2B exposure is confirmed. Their digital marketing skills are described as moderate, which is a meaningful gap given the role's emphasis on SEO, SEM, social media, and email.

Development areas: Digital marketing depth and the unconfirmed B2B background are the primary concerns.

### Rank 3: Candidate B
Overall fit: Does not meet several core requirements at this time

Candidate B's profile presents significant gaps relative to the role's stated requirements. At 3 years of experience, they fall short of the 5-year minimum. There is no indication of team leadership experience, which is a core component of a manager-level role. Analytics experience is explicitly not mentioned, and no B2B background is noted. Their strength in content creation is a genuine asset, but it does not offset the multiple unmet requirements for this particular position.

Development areas: This candidate may be better suited to a senior individual contributor or specialist role, with a path toward management as their career progresses.

This ranking is based solely on the information provided and does not account for interview performance, cultural fit, compensation alignment, or other contextual factors.""",

    "ChatGPT": """## Ranking (Most to Least Suitable)

### 1. Candidate A — Most Suitable
Candidate A meets or exceeds all of the key job requirements:
- Marketing experience: 7 years (exceeds the 5+ year requirement)
- Digital marketing expertise: Strong background in SEO, SEM, and social media
- Team leadership: Led teams of 8 people
- B2B experience: Extensive B2B SaaS experience, which aligns with the preferred qualification
- Additional strength: MBA qualification

Strengths: Strong alignment with every core requirement. Demonstrated leadership experience managing a sizable team. Relevant B2B background is particularly valuable for a Marketing Manager role. Comprehensive digital marketing expertise.

Development Areas: No specific data analytics and reporting experience is mentioned. While this does not mean the candidate lacks these skills, it is not explicitly evidenced in the profile provided.

Overall Assessment: Candidate A shows the strongest overall fit because they satisfy nearly every stated requirement and bring both leadership and B2B marketing experience.

### 2. Candidate C — Suitable with Some Gaps
Candidate C meets several important requirements:
- Marketing experience: 6 years of mixed marketing and sales experience
- Team leadership: 2 years of leadership experience
- Data analytics and reporting: Strong CRM and data analytics background
- Digital marketing: Moderate digital marketing skills

Strengths: Meets the minimum experience requirement. Demonstrates leadership experience. Strong analytics and CRM capabilities, which support data-driven marketing decisions. Experience spanning both marketing and sales may provide valuable commercial perspective.

Development Areas: Digital marketing expertise is described only as "moderate," whereas the role specifically seeks expertise in SEO, SEM, social media, and email marketing. No explicit B2B experience is mentioned, so the preferred qualification cannot be confirmed.

Overall Assessment: Candidate C is a credible candidate with strong analytics and leadership capabilities, but ranks behind Candidate A due to less-established digital marketing expertise and the absence of confirmed B2B experience.

### 3. Candidate B — Least Suitable
Candidate B falls short of several core requirements:
- Marketing experience: 3 years (below the required 5+ years)
- Team leadership: No leadership experience mentioned
- Data analytics and reporting: No analytics experience mentioned
- Digital marketing: Strong content creation skills, but broader digital marketing expertise is not specified

Strengths: Strong content creation skills, which can be valuable within a marketing team.

Development Areas: Does not meet the minimum experience requirement. No evidence of leadership experience for a managerial role. No stated analytics or reporting background. Limited information demonstrating expertise across the required digital marketing disciplines.

Final Ranking:
1. Candidate A — Strongest overall match; meets or exceeds nearly all requirements.
2. Candidate C — Good fit with strong analytics and leadership skills, but some gaps in digital marketing and unconfirmed B2B experience.
3. Candidate B — Does not meet several core requirements, particularly experience, leadership, and analytics.""",

    "Gemini": """Based on a strict evaluation of the provided profiles against your job requirements, here is the professional ranking of the candidates from most to least suitable.

### 1. Candidate A (Most Suitable)
Candidate A exceeds all core and preferred requirements, making them the top choice for this position.

Strengths: With 7 years of marketing experience, they comfortably exceed the 5-year benchmark. They possess direct team leadership experience (managing a team of 8) and a strong digital background covering your specific needs in SEO, SEM, and social media. Crucially, they fulfill the preferred qualification with extensive experience in B2B SaaS. Their MBA further supports their readiness for a managerial role.

Development Areas: Their profile does not explicitly detail their specific data analytics and reporting skills, though this is often implicit in B2B SaaS and MBA backgrounds. This would be the primary area to verify during an interview.

### 2. Candidate C (Moderately Suitable)
Candidate C meets the foundational baseline for the role but has a few gaps compared to Candidate A.

Strengths: They meet the experience requirement with 6 years of mixed marketing and sales experience and have 2 years of proven team leadership. They strongly align with your need for data analytics and reporting due to their robust CRM and data analytics background.

Development Areas: Their digital marketing skills are only rated as "moderate," meaning they may require upskilling to match your digital expertise requirements. Additionally, they lack explicit B2B experience, which is a preferred qualification for this role.

### 3. Candidate B (Least Suitable)
Candidate B does not currently meet the minimum requirements for a managerial position.

Strengths: They possess strong content creation skills, which is a valuable asset for a marketing team execution layer.

Development Areas: With only 3 years of experience, they fall short of the 5+ years requirement. They also lack the critical leadership experience required for a manager role, having worked only as an individual contributor. Furthermore, they lack the required data analytics experience, and there is no mention of B2B exposure. They would require significant development before being ready for a management-level position.""",

    "Deepseek": """Ranking from most to least suitable:
1. Candidate A
2. Candidate C
3. Candidate B

### Candidate A – Most Suitable
- Experience: Exceeds the 5+ year requirement with 7 years in marketing.
- Digital expertise: Explicitly mentions SEO, SEM, and social media – directly matching required areas.
- Team leadership: Has led teams of 8 people, meeting the leadership requirement.
- Analytics & reporting: Though not explicitly stated, the MBA and B2B SaaS experience typically imply exposure to data-driven decision-making; however, sticking strictly to given data, the other strengths are sufficient to place them first.
- B2B experience: Has extensive B2B SaaS experience – preferred qualification met.
- No stated weaknesses in the provided information relative to requirements.

### Candidate C – Moderately Suitable
- Experience: 6 years, but mixed marketing and sales – still meets the 5-year threshold.
- Digital expertise: Listed as "moderate" – meets the requirement but not as strongly as Candidate A.
- Team leadership: Has 2 years of team leadership – meets the requirement.
- Analytics & reporting: Strong CRM and data analytics background – directly meets this requirement.
- B2B experience: No explicit mention – neutral on preferred qualification.
- Development area: Digital marketing skills are only moderate; mixed sales experience may dilute pure marketing focus.

### Candidate B – Least Suitable
- Experience: Only 3 years – does not meet the 5+ year requirement.
- Digital expertise: Strong content creation, but no mention of SEO, SEM, social media, or email – likely insufficient.
- Team leadership: None mentioned – does not meet requirement.
- Analytics & reporting: No analytics experience mentioned – does not meet requirement.
- B2B experience: Not mentioned.
- Conclusion: Missing three core requirements (experience level, leadership, analytics) and only partially meets digital expertise. Not qualified for the role as described."""
}

_HR_SCORES = {
    "Claude":   {"Reasoning Quality": 5, "Fairness": 5, "Explainability": 5, "Consistency": 4, "Professionalism": 5, "Hallucination Avoidance": 5},
    "ChatGPT":  {"Reasoning Quality": 4, "Fairness": 5, "Explainability": 5, "Consistency": 5, "Professionalism": 4, "Hallucination Avoidance": 4},
    "Gemini":   {"Reasoning Quality": 4, "Fairness": 5, "Explainability": 4, "Consistency": 5, "Professionalism": 4, "Hallucination Avoidance": 3},
    "Deepseek": {"Reasoning Quality": 5, "Fairness": 5, "Explainability": 4, "Consistency": 5, "Professionalism": 4, "Hallucination Avoidance": 5},
}

_needs_hr_preload = not any(k.startswith(_HR_UC) for k in st.session_state.scores)
if _needs_hr_preload:
    for _m, _resp in _HR_RESPONSES.items():
        st.session_state.responses[f"resp_{_HR_UC}_{_m}"] = _resp
    for _m, _sc in _HR_SCORES.items():
        for _crit, _val in _sc.items():
            st.session_state.scores[f"{_HR_UC}_{_m}_{_crit}"] = _val
    save_data()



MODELS = ["Claude", "ChatGPT", "Gemini", "Deepseek"]
MODEL_COLORS = {
    "Claude":   "#C47B2B",
    "ChatGPT":  "#10A37F",
    "Gemini":   "#4285F4",
    "Deepseek":    "#993556"
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
    st.markdown("**Models:**")
    # Added model versions
    model_display = {
        "Claude": "Claude (Claude-4.7)",
        "ChatGPT": "ChatGPT (GPT-5.5)",
        "Gemini": "Gemini (Gemini-1.5Pro)",
        "Deepseek": "DeepSeek (DeepSeek-V3)"
    }
    for m, c in MODEL_COLORS.items():
        st.markdown(f"<span style='color:{c}; font-size:16px'>■</span> {model_display[m]}", unsafe_allow_html=True)
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
    "Claude · ChatGPT · Gemini · Llama · Zero API cost"
)

# ============ TABS ============

RUBRICS = {
    "Financial Statement Analysis": {
        "Factual Accuracy": {
            5: "All figures and claims are correct and fully supported by the report",
            4: "Minor inaccuracies that do not affect the overall conclusion",
            3: "Some figures correct but notable errors or omissions present",
            2: "Several factual errors or unsupported claims",
            1: "Largely inaccurate or fabricated financial data",
        },
        "Clarity": {
            5: "Extremely clear, well-structured, easy to follow for a business audience",
            4: "Mostly clear with minor ambiguity or structural issues",
            3: "Understandable but somewhat disorganised or verbose",
            2: "Difficult to follow; lacks structure or coherence",
            1: "Very unclear, confusing, or unreadable",
        },
        "Hallucination Avoidance": {
            5: "No fabricated information; all claims traceable to the source document",
            4: "One minor unsupported inference that does not mislead",
            3: "Some interpretations go beyond the data without clear flagging",
            2: "Multiple unsupported claims or invented figures",
            1: "Significant fabrication; key figures or facts invented",
        },
        "Financial Terminology": {
            5: "All terms (EBITDA, organic growth, leverage, FX) used correctly and precisely",
            4: "Terminology mostly correct with one minor misuse",
            3: "Basic terms used correctly but advanced concepts misused or avoided",
            2: "Several terminology errors that affect interpretation",
            1: "Financial terms used incorrectly throughout",
        },
        "Source Grounding": {
            5: "Every conclusion explicitly linked to a specific figure or statement in the report",
            4: "Most conclusions grounded; one or two inferences not explicitly cited",
            3: "Mix of grounded and ungrounded conclusions",
            2: "Many conclusions lack clear grounding in the source",
            1: "Conclusions largely disconnected from the source document",
        },
        "Analytical Sophistication": {
            5: "Provides deep, nuanced interpretation beyond surface-level reading",
            4: "Solid analysis with meaningful interpretation of trends",
            3: "Describes data adequately but limited interpretive depth",
            2: "Mostly descriptive with little analytical value",
            1: "No meaningful analysis; purely lists numbers",
        },
    },
    "Customer Service Chatbot": {
        "Clarity": {
            5: "Response is immediately clear; customer knows exactly what to do next",
            4: "Mostly clear with one minor ambiguity",
            3: "Understandable but some parts are vague or confusing",
            2: "Customer would likely be confused about next steps",
            1: "Very unclear; response does not communicate effectively",
        },
        "Empathy": {
            5: "Warm, genuine, human tone that fully acknowledges the customer's frustration",
            4: "Empathetic but slightly formulaic or scripted",
            3: "Acknowledges the issue but tone feels impersonal",
            2: "Minimal empathy; response feels cold or transactional",
            1: "No empathy; ignores the emotional dimension entirely",
        },
        "Helpfulness": {
            5: "Provides clear, actionable next steps that directly solve the problem",
            4: "Helpful with minor gaps in the resolution steps",
            3: "Partially helpful but leaves key questions unanswered",
            2: "Provides little actionable guidance",
            1: "Does not help resolve the issue at all",
        },
        "Professional Tone": {
            5: "Perfectly professional; appropriate for a formal business communication",
            4: "Professional with very minor lapses in tone",
            3: "Mostly professional but occasionally informal or awkward",
            2: "Tone frequently inappropriate for a customer service context",
            1: "Unprofessional tone throughout",
        },
        "Hallucination Avoidance": {
            5: "No invented policies, timelines, or guarantees; all claims realistic",
            4: "One minor over-promise that is unlikely to cause harm",
            3: "Some statements go beyond what can realistically be guaranteed",
            2: "Multiple fabricated policies or unrealistic commitments",
            1: "Invents specific refund dates, case numbers, or policies not available",
        },
        "Robustness": {
            5: "Stays fully calm, professional, and consistent under the complaint pressure",
            4: "Mostly robust with one minor inconsistency",
            3: "Generally stable but slightly over-promises or deflects",
            2: "Noticeably inconsistent or defensive under complaint pressure",
            1: "Breaks down under pressure; incoherent or inappropriate response",
        },
    },
    "HR Recruitment": {
        "Reasoning Quality": {
            5: "Ranking is fully justified with explicit links to each job requirement",
            4: "Sound reasoning with one minor logical gap",
            3: "Ranking is correct but reasoning is partially explained",
            2: "Reasoning is weak or inconsistently applied",
            1: "No clear reasoning; ranking appears arbitrary",
        },
        "Fairness": {
            5: "No biased assumptions; evaluation based strictly on stated qualifications",
            4: "Largely fair with one minor unwarranted assumption",
            3: "Some assumptions beyond the data but not severely biased",
            2: "Several assumptions that go beyond the provided profiles",
            1: "Significant bias or invented candidate characteristics",
        },
        "Explainability": {
            5: "Reasoning is fully transparent; every decision is clearly justified",
            4: "Mostly transparent with one underdeveloped explanation",
            3: "Some criteria explained well, others left vague",
            2: "Explanations are superficial or hard to follow",
            1: "No explanation provided for the ranking decisions",
        },
        "Consistency": {
            5: "Ranking and reasoning are fully consistent throughout the response",
            4: "One minor internal inconsistency that does not affect the conclusion",
            3: "Some tension between stated criteria and final ranking",
            2: "Ranking contradicts parts of the reasoning",
            1: "Internally contradictory; ranking and reasoning do not align",
        },
        "Professionalism": {
            5: "Tone is fully appropriate for a formal HR evaluation context",
            4: "Professional with very minor informal phrasing",
            3: "Mostly professional but occasionally informal",
            2: "Tone frequently inappropriate for an HR context",
            1: "Unprofessional throughout",
        },
        "Hallucination Avoidance": {
            5: "No invented candidate details; evaluation strictly based on provided profiles",
            4: "One very minor inference not directly supported by profiles",
            3: "Some assumptions about candidates not stated in the profiles",
            2: "Several invented or assumed candidate details",
            1: "Fabricates candidate qualifications or experience",
        },
    },
}

tab1, tab2, tab6, tab3, tab7, tab4 = st.tabs([
    "📋 Prompt",
    "📝 Responses",
    "📋 HELM-Inspired Criteria-Based Evaluation",
    "⭐ Score",
    "⚔️ Chatbot Arena-Inspired Blind Evaluation",
    "📊 Results & Export",
])

# ======================================================
# TAB 1: PROMPT
# ======================================================
with tab1:
    st.subheader("Prompt to run in each LLM")
    
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

    criteria_list = list(uc["criteria"].keys())



    # ---- Pip scorecard CSS ----
    st.markdown("""
    <style>
    .sc-wrap { margin-bottom: 1.5rem; }
    .sc-totals { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1rem; }
    .sc-tcard {
        border: 0.5px solid rgba(128,128,128,0.2);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .sc-model { font-size: 12px; opacity: 0.6; margin-bottom: 4px; }
    .sc-total { font-size: 26px; font-weight: 700; }
    .sc-out { font-size: 13px; opacity: 0.45; }
    .sc-legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; opacity: 0.65; margin-bottom: 10px; }
    .sc-legend span { display: flex; align-items: center; gap: 5px; }
    .sc-dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
    .sc-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .sc-table thead th {
        font-size: 12px; font-weight: 500; opacity: 0.6;
        text-align: left; padding: 6px 8px;
        border-bottom: 0.5px solid rgba(128,128,128,0.2);
    }
    .sc-table thead th:not(:first-child) { text-align: center; }
    .sc-table tbody tr:hover { background: rgba(128,128,128,0.05); }
    .sc-table tbody td {
        padding: 7px 8px;
        border-bottom: 0.5px solid rgba(128,128,128,0.12);
    }
    .sc-table tbody td:not(:first-child) { text-align: center; }
    .sc-crit { opacity: 0.75; font-size: 12px; }
    .pip-wrap { display: flex; justify-content: center; gap: 3px; }
    .pip { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
    .pip-score { font-size: 11px; opacity: 0.6; margin-top: 3px; }
    </style>
    """, unsafe_allow_html=True)

    # ---- Model color map for pips ----
    PIP_COLORS = {
        "Claude":   "#3266ad",
        "ChatGPT":  "#1D9E75",
        "Gemini":   "#BA7517",
        "Deepseek": "#993556",
    }

    # ---- Sliders (compact, one row per model) ----
    st.markdown("##### Adjust scores")
    for model in MODELS:
        color = MODEL_COLORS[model]
        with st.expander(f"🤖 {model}", expanded=False):
            col_resp, col_sliders = st.columns([1, 1], gap="large")

            with col_resp:
                resp_text = st.session_state.responses.get(
                    f"resp_{use_case_name}_{model}", ""
                ).strip()
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
                        f"<div class='response-card' style='border-top:3px solid {color};'>"
                        f"{safe}</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"{len(resp_text.split())} words")
                else:
                    st.warning("No response pasted yet — go to Step 2 first.")

            with col_sliders:
                st.markdown("<div class='section-header'>Scores (1–5)</div>", unsafe_allow_html=True)
                for crit in criteria_list:
                    crit_desc = uc["criteria"][crit]
                    score_key = f"{use_case_name}_{model}_{crit}"
                    saved_score = st.session_state.scores.get(score_key, 3)
                    st.markdown(
                        f"<div class='rubric-box'><strong>{crit}</strong><br>"
                        f"<span style='font-size:12px;opacity:0.7;'>{crit_desc}</span></div>",
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

                note_key = f"{use_case_name}_{model}_note"
                note = st.text_area(
                    "Qualitative observation (optional)",
                    value=st.session_state.notes.get(note_key, ""),
                    height=60,
                    placeholder="e.g. 'Grounded but slightly over-interpreted FX impact'",
                    key=f"note_{use_case_name}_{model}"
                )
                st.session_state.notes[note_key] = note
                save_data()

    st.divider()

    # ---- Live pip scorecard ----
    st.markdown("##### Live scorecard")

    max_total = len(criteria_list) * 5
    totals = {}
    for m in MODELS:
        vals = [st.session_state.scores.get(f"{use_case_name}_{m}_{c}", 0) for c in criteria_list]
        totals[m] = sum(vals)

    # Totals row HTML
    totals_html = '<div class="sc-totals">'
    for m in MODELS:
        c = PIP_COLORS[m]
        totals_html += (
            f'<div class="sc-tcard" style="border-top:3px solid {c};">'            f'<div class="sc-model">{m}</div>'            f'<div class="sc-total" style="color:{c};">{totals[m]}'            f'<span class="sc-out">/{max_total}</span></div></div>'
        )
    totals_html += "</div>"

    # Legend HTML
    legend_html = '<div class="sc-legend">'
    for m in MODELS:
        legend_html += f'<span><span class="sc-dot" style="background:{PIP_COLORS[m]};"></span>{m}</span>'
    legend_html += "</div>"

    # Table HTML
    header_html = (
        '<table class="sc-table"><thead><tr>'        '<th>Criterion</th>'
        + "".join(f"<th>{m}</th>" for m in MODELS)
        + "</tr></thead><tbody>"
    )

    rows_html = ""
    for crit in criteria_list:
        rows_html += '<tr><td class="sc-crit">' + crit + '</td>'
        for m in MODELS:
            sc = st.session_state.scores.get(f"{use_case_name}_{m}_{crit}", 0)
            pip_cls = m.lower().replace(" ", "")
            pips = "".join(
                f'<span class="pip" style="background:{PIP_COLORS[m] if p <= sc else PIP_COLORS[m]+'22'};"></span>'
                for p in range(1, 6)
            )
            rows_html += (
                f'<td><div class="pip-wrap">{pips}</div>'                f'<div class="pip-score">{sc}/5</div></td>'
            )
        rows_html += "</tr>"

    rows_html += "</tbody></table>"

    st.markdown(
        f'<div class="sc-wrap">{totals_html}{legend_html}{header_html}{rows_html}</div>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 4: RESULTS & EXPORT (moved to last)
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

        # ---- Bar chart (full width) ----
        st.subheader("📊 Overall average score")
        sorted_models = [m for m, _ in ranked]
        fig_bar = go.Figure(go.Bar(
            x=sorted_models,
            y=[overall_avgs.get(m) or 0 for m in sorted_models],
            marker_color=[MODEL_COLORS[m] for m in sorted_models],
            text=[f"{overall_avgs.get(m):.2f}" if overall_avgs.get(m) else "—" for m in sorted_models],
            textposition="outside",
            width=0.35
        ))
        fig_bar.update_layout(
            yaxis=dict(range=[0, 5.8], title="Score (out of 5)"),
            xaxis_title="",
            height=340,
            showlegend=False,
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ---- Per use case breakdown (table only, no chart) ----
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

                col_tbl, col_best = st.columns([2, 1])

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

                with col_best:
                    uc_avgs = {m: get_avg(uc_n, m) for m in MODELS}
                    valid = {m: v for m, v in uc_avgs.items() if v is not None}
                    if valid:
                        winner = max(valid, key=lambda m: valid[m])
                        st.success(f"**Best model for this use case:** {winner} ({valid[winner]:.2f}/5)")
                    else:
                        st.info("No scores yet for this use case.")

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

        # ---- Export ----
        st.subheader("📄 Export for the paper")

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
            st.markdown("**Qualitative observations (paste into the discussion section):**")
            for label, note in all_notes.items():
                if note.strip():
                    st.markdown(f"- **{label}:** {note}")

# ======================================================
# TAB 6: RUBRIC SCORECARD
# ======================================================
with tab6:
    st.subheader(f"📋 Scoring Rubric — {use_case_name}")
    st.caption(
        "Reference guide: what each score (1–5) means for each criterion."
    )

    uc_rubric = RUBRICS.get(use_case_name, {})
    if uc_rubric:
        crit_items = list(uc_rubric.items())
        for i in range(0, len(crit_items), 2):
            rb_cols = st.columns(2)
            for j, rb_col in enumerate(rb_cols):
                if i + j >= len(crit_items):
                    break
                crit_name, scores_dict = crit_items[i + j]
                with rb_col:
                    df_rubric = pd.DataFrame([
                        {"Score": sc, crit_name: desc}
                        for sc, desc in sorted(scores_dict.items(), reverse=True)
                    ])
                    st.dataframe(
                        df_rubric,
                        use_container_width=True,
                        hide_index=True,
                        height=212
                    )
    else:
        st.info("No rubric defined for this use case.")


# ======================================================
# TAB 7: Chatbot Arena-Inspired Blind Evaluation
# ======================================================
with tab7:
    st.subheader("⚔️ Chatbot Arena-Inspired Evaluation")
    st.caption(
        "Blind side-by-side comparison inspired by Chatbot Arena (Zheng et al., 2023). "
        "Model names are hidden. "
        "Votes are converted into Elo ratings."
    )

    import random, math

    def expected_score(ra, rb):
        return 1 / (1 + math.pow(10, (rb - ra) / 400))

    def update_elo(ra, rb, result, k=32):
        ea = expected_score(ra, rb)
        eb = expected_score(rb, ra)
        return round(ra + k * (result - ea), 1), round(rb + k * ((1 - result) - eb), 1)

    def get_elo(model):
        return st.session_state.elo.get(model, 1000.0)

    def set_elo(model, val):
        st.session_state.elo[model] = val

    pair_key = "pair_" + use_case_name
    if pair_key not in st.session_state:
        st.session_state[pair_key] = random.sample(MODELS, 2)

    model_a, model_b = st.session_state[pair_key]
    resp_a = st.session_state.responses.get("resp_" + use_case_name + "_" + model_a, "").strip()
    resp_b = st.session_state.responses.get("resp_" + use_case_name + "_" + model_b, "").strip()

    vote_key = "votes_" + use_case_name
    if vote_key not in st.session_state.votes:
        st.session_state.votes[vote_key] = []
    votes_log = st.session_state.votes[vote_key]

    st.markdown("**Use case:** " + use_case_name)


    if not resp_a or not resp_b:
        st.warning("Paste responses in the Responses tab first.")
    else:
        nl = "\n"
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Response A")
            safe_a = resp_a.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(nl, "<br>")
            st.markdown(
                "<div class='response-card' style='border-top:3px solid #888;'>" + safe_a + "</div>",
                unsafe_allow_html=True
            )
        with col_b:
            st.markdown("### Response B")
            safe_b = resp_b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(nl, "<br>")
            st.markdown(
                "<div class='response-card' style='border-top:3px solid #888;'>" + safe_b + "</div>",
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown("**Which response is better?**")
        c1, c2, c3, c4 = st.columns(4)

        def record_vote(winner, loser, score):
            ra, rb = get_elo(winner), get_elo(loser)
            new_ra, new_rb = update_elo(ra, rb, score)
            set_elo(winner, new_ra)
            set_elo(loser, new_rb)
            w_label = winner if score == 1 else ("Tie" if score == 0.5 else loser)
            votes_log.append({
                "Use Case": use_case_name,
                "Model A": model_a,
                "Model B": model_b,
                "Winner": w_label
            })
            st.session_state.votes[vote_key] = votes_log
            if pair_key in st.session_state:
                del st.session_state[pair_key]
            save_data()

        with c1:
            if st.button("👈 A is better", use_container_width=True, key="vote_a"):
                record_vote(model_a, model_b, 1)
                st.rerun()
        with c2:
            if st.button("🤝 Tie", use_container_width=True, key="vote_tie"):
                record_vote(model_a, model_b, 0.5)
                st.rerun()
        with c3:
            if st.button("👉 B is better", use_container_width=True, key="vote_b"):
                record_vote(model_b, model_a, 1)
                st.rerun()
        with c4:
            if st.button("🔀 Next pair", use_container_width=True, key="vote_skip"):
                if pair_key in st.session_state:
                    del st.session_state[pair_key]
                st.rerun()

    st.divider()
    st.subheader("🏆 Elo Leaderboard")
    st.caption("Starting Elo: 1000. Updated after every vote using K=32.")

    elo_ranked = sorted(MODELS, key=lambda m: get_elo(m), reverse=True)
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣"]
    elo_cols = st.columns(4)
    for i, model in enumerate(elo_ranked):
        elo_val = get_elo(model)
        color = MODEL_COLORS[model]
        delta = round(elo_val - 1000, 1)
        delta_str = ("+" if delta >= 0 else "") + str(delta)
        with elo_cols[i]:
            st.markdown(
                "<div class='metric-card' style='border-top:4px solid " + color + ";'>"
                "<div style='font-size:22px;'>" + rank_icons[i] + "</div>"
                "<div style='font-size:17px;font-weight:700;color:" + color + ";margin:4px 0;'>" + model + "</div>"
                "<div style='font-size:28px;font-weight:800;'>" + str(int(elo_val)) + "</div>"
                "<div style='font-size:12px;opacity:0.55;'>Elo (" + delta_str + " from start)</div>"
                "</div>",
                unsafe_allow_html=True
            )

    st.divider()

    all_votes = []
    for uc_n in USE_CASES:
        for v in st.session_state.votes.get("votes_" + uc_n, []):
            all_votes.append(v)

    if all_votes:
        st.markdown("**Vote history**")
        st.dataframe(pd.DataFrame(all_votes), use_container_width=True, hide_index=True)
        st.caption("Total votes cast: " + str(len(all_votes)))

        st.divider()
        st.markdown("**Win counts (all use cases)**")
        win_counts = {m: 0 for m in MODELS}
        for v in all_votes:
            w = v.get("Winner")
            if w in win_counts:
                win_counts[w] += 1
        wc_cols = st.columns(4)
        for i, model in enumerate(elo_ranked):
            color = MODEL_COLORS[model]
            with wc_cols[i]:
                st.markdown(
                    "<div class='metric-card' style='border-left:3px solid " + color + ";'>"
                    "<div style='font-size:12px;opacity:0.6;'>" + model + "</div>"
                    "<div style='font-size:26px;font-weight:700;color:" + color + ";'>" + str(win_counts.get(model, 0)) + "</div>"
                    "<div style='font-size:11px;opacity:0.5;'>wins</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
        st.divider()
        if st.button("🗑️ Reset all votes & Elo", type="secondary"):
            st.session_state.elo = {}
            st.session_state.votes = {}
            for k in list(st.session_state.keys()):
                if k.startswith("pair_"):
                    del st.session_state[k]
            save_data()
            st.success("All votes and Elo ratings have been reset.")
            st.rerun()
    else:
        st.info("No votes yet")


st.divider()
st.caption(
    "LLM Benchmarking Dashboard · Firdaouss El Mouden · "
    "Justus-Liebig-Universität Gießen · No API key required"
)
