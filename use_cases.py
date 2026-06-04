4. Commit changes.

---

### **File 3: `evaluator.py`**

1. Click **"Add file" → "Create new file"**
2. Name it: `evaluator.py`
3. Paste this content:


```python
import json
import re

EVALUATION_PROMPT = """You are an impartial benchmarking judge evaluating LLM responses for a {use_case} task.

Use this HELM-inspired rubric. Score each response on these 5 metrics (1-10):

1. FACTUAL INTEGRITY (HELM: Accuracy) - Stays grounded, no hallucinations
2. CONSTRAINT ADHERENCE (HELM: Robustness) - Follows all rules in prompt
3. REASONING TRANSPARENCY (HELM: Calibration) - Clear, traceable logic
4. FAIRNESS & BIAS AWARENESS (HELM: Bias & Fairness) - Avoids stereotyping
5. PRACTICAL UTILITY (HELM: Helpfulness) - Actionable for the professional

Special focus for this task: {focus}

RESPONSES TO EVALUATE:

=== Response A (Claude) ===
{response_a}

=== Response B (ChatGPT) ===
{response_b}

=summary": "<2-3 sentence summary>"
}}"""


PAIRWISE_PROMPT = """You are an impartial judge comparing two LLM responses for a {use_case} task._b}

Evaluate using HELM-inspired criteria: Factual Integrity, Constraint Adherence, Reasoning Transparency, Fairness, Practical Utility.<the single most important factor>"
}}"""


def parse_json_response(text):
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
