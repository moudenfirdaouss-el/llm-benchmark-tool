import json
import re

# ============ ABSOLUTE SCORING PROMPT (HELM-Inspired) ============
EVALUATION_PROMPT = """You are an impartial benchmarking judge evaluating LLM responses for a {use_case} task.

Use this HELM-inspired rubric. Score each response on these 5 metrics (1-10 scale):

1. FACTUAL INTEGRITY (HELM: Accuracy)
   - Stays grounded in source material
   - No hallucinated facts, numbers, or relationships
   - Acknowledges missing data when appropriate

2. CONSTRAINT ADHERENCE (HELM: Robustness)
   - Follows all explicit rules in the prompt
   - Respects stated boundaries and policies
   - Maintains performance under pressure or ambiguity

3. REASONING TRANSPARENCY (HELM: Calibration)
   - Logic is explicit and traceable
   - Uncertainty is expressed appropriately
   - Distinguishes facts from inferences

4. FAIRNESS & BIAS AWARENESS (HELM: Bias & Fairness)
   - Avoids stereotyping or demographic bias
   - Self-checks for cognitive biases
   - Provides balanced framing

5. PRACTICAL UTILITY (HELM: Helpfulness + Efficiency)
   - Actionable for the target professional
   - Well-structured and appropriately concise
   - Domain-appropriate tone and depth

Special focus for this task: {focus}

RESPONSES TO EVALUATE:

=== Response A (Claude) ===
{response_a}

=== Response B (ChatGPT) ===
{response_b}

=== Response C (Gemini) ===
{response_c}

Return ONLY a valid JSON object in this exact format (-10>,
    "justification": "<2-3 sentence explanation>"
  }},
  "summary": "<2-3 sentence overall comparison summary>"
}}"""


# ============ PAIRWISE COMPARISON PROMPT (MT-Bench Style) ============
PAIRWISE_PROMPT = """You are an impartial judge comparing two LLM responses for a {use_case} task.

ORIGINAL PROMPT GIVEN TO BOTH MODELS:
{original_prompt}

RESPONSE A ({name_a}):
{response_a}

RESPONSE B ({name_b}):
{response_b}

Evaluate which response is better using these HELM-inspired criteria:
1. Factual Integrity (accuracy, no hallucinations)
2. Constraint Adherence (follows the prompt's rules)
3. Reasoning Transparency (clear, traceable logic)
4. Fairness & Bias Awareness (balanced, unbiased framing)
5. Practical Utility (actionable, professional-grade)

IMPORTANT INSTRUCTIONS:
- Be objective and avoid position bias (don't favor A just because it's listed first)
- Consider all 5 criteria holistically
- If the responses are roughly equal in quality, declare a tie
- Base your jud<the single most important factor that decided the match>"
}}"""


# ============ JSON PARSER ============
def parse_json_response(text):
    """
    Extract JSON from an LLM response.
    Handles cases where the model wraps JSON in markdown code blocks
    or includes extra text before/after the JSON.
    """
    if not text:
        return None
    
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try direct JSON parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Fallback: extract the first JSON object found in the text
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    
    # If all parsing fails, return None
    return None
