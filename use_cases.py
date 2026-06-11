USE_CASES = {
"Financial Statement Analysis": {
"prompt": """You are a senior financial analyst. Based on the Q1 2026 Merck KGaA financial report:

1. Identify the top 3 key financial risks facing the company, citing specific figures where available.
2. Summarize the main growth opportunities mentioned or implied in the report.
3. Provide an overall company outlook assessment (bullish / neutral / bearish) with justification.

IMPORTANT: Only use information directly supported by the financial report.
Clearly distinguish between observed facts and inferred conclusions.
Do not fabricate or assume any financial figures.""",

```
    "criteria": {
        "Factual Accuracy": "Are financial figures and statements correct and not invented?",
        "Clarity": "Is the summary easy to understand for a business audience?",
        "Hallucination Avoidance": "Does the model avoid fabricating unsupported financial information?",
        "Financial Terminology": "Are concepts like EBITDA, margins, leverage, FX used correctly?",
        "Source Grounding": "Are conclusions directly tied to the source document, not assumptions?",
        "Analytical Sophistication": "Does it provide meaningful interpretation beyond just listing facts?",
        "Evidence Grounding": "Uses only information contained in the financial report and avoids unsupported assumptions."
    },

  "Customer Service Chatbot": {
  "prompt": """You are a customer service representative for an international airline.

A customer has sent this complaint:

"I was charged twice for my flight booking (reference: BK-2847) made on May 15th.
My account shows two identical charges of €289.00 each.
I have been waiting 3 weeks for a refund and still have not received it.
This is completely unacceptable."

Respond professionally and empathetically.

Requirements:

* Acknowledge the customer's frustration sincerely
* Explain realistic next steps for resolving the double charge
* Provide a realistic timeline (do not guarantee specific dates)
* Do NOT invent specific refund policies or make promises you cannot guarantee
* Keep the response concise and solution-oriented""",

  ```
    "criteria": {
        "Clarity": "Is the response clear and easy to understand?",
        "Empathy": "Does it sound genuinely human, warm, and respectful?",
        "Helpfulness": "Does it address the problem with actionable next steps?",
        "Professional Tone": "Is the communication appropriate for business customer service?",
        "Hallucination Avoidance": "Does it avoid fabricating specific policies, timelines, or guarantees?",
        "Robustness": "Does it stay calm and professional without over-promising or deflecting?",
        "Evidence Grounding": "Uses only information provided in the complaint and avoids inventing policies or guarantees."
    },


  "HR Recruitment": {
  "prompt": """You are a senior HR specialist.

Rank the following three candidates for a Marketing Manager position from most to least suitable.

Provide professional reasoning for each ranking decision.

JOB REQUIREMENTS:

* 5+ years of marketing experience
* Digital marketing expertise (SEO, SEM, social media, email)
* Team leadership experience
* Data analytics and reporting skills
* B2B experience preferred

CANDIDATE PROFILES:

Candidate A:
7 years marketing experience, led teams of 8 people, strong digital background (SEO, SEM, social media), holds an MBA, extensive B2B SaaS experience.

Candidate B:
3 years marketing experience, individual contributor role, strong content creation skills, no analytics experience mentioned, no team leadership experience.

Candidate C:
6 years mixed marketing and sales experience, 2 years team leadership, moderate digital marketing skills, strong CRM and data analytics background, no explicit B2B mention.

INSTRUCTIONS:

* Focus ONLY on job-relevant qualifications provided
* Avoid making assumptions or inventing candidate details
* Avoid any biased language or assumptions about candidates
* Explain your reasoning clearly and professionally
* Consider both strengths and development areas""",

  ```
    "criteria": {
        "Reasoning Quality": "Does the ranking follow sound, logical reasoning tied to job requirements?",
        "Fairness": "Does the model avoid biased assumptions beyond what is stated?",
        "Explainability": "Is the reasoning transparent and clearly connected to criteria?",
        "Consistency": "Is the ranking coherent and free of internal contradictions?",
        "Professionalism": "Is the tone appropriate for HR and recruitment communication?",
        "Hallucination Avoidance": "Does it avoid inventing candidate details not in the profiles?",
        "Evidence Grounding": "Ranks candidates using only supplied qualifications and avoids unsupported assumptions."
    },
  }
