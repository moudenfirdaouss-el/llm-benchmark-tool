USE_CASES = {
    "Financial Statement Analysis": {
        "prompt": """You are an expert Financial Analyst. Analyze the following provided financial data and identify:
1. Key revenue trends.
2. Any significant discrepancies between cash flow and net income.
3. Potential financial risks.

Data:
Revenue 2022: $10M, Revenue 2023: $12M
Net Income 2022: $1M, Net Income 2023: $1.5M
Operating Cash Flow 2022: $1.2M, Operating Cash Flow 2023: $0.8M

Provide a structured report with clear reasoning.""",
        "focus": "Accuracy in figure interpretation, identifying cash flow discrepancies, and professional tone."
    },
    "Customer Service Chatbot": {
        "prompt": """You are a Customer Service Representative for 'EcoStore'. 
Policy: We offer a 5-day return window for all products. We can provide a $25 voucher for inconveniences, but cannot offer full refunds after 5 days.

Customer Message: 'I bought a plant 7 days ago and it died! This is ridiculous. I want my money back immediately or I am calling my lawyer!'

Respond to the customer following the policy strictly while maintaining a professional and de-escalating tone.""",
        "focus": "Policy adherence, emotional intelligence, and maintaining professional boundaries."
    },
    "HR Recruitment Assistant": {
        "prompt": """You are an HR Recruitment Assistant. Evaluate the following two candidates for a Senior Developer role based on the criteria provided.

Criteria: 
- Technical Expertise (Weight: 50%)
- Leadership Experience (Weight: 30%)
- Communication (Weight: 20%)

Candidate A: 10 years experience, expert in Python, led a team of 5, excellent communicator.
Candidate B: 4 years experience, expert in JavaScript, no leadership experience, good communication.

Provide a weighted decision matrix and a final recommendation for which candidate to interview.""",
        "focus": "Bias awareness, logical weighting, and structured decision-making."
    }
}
