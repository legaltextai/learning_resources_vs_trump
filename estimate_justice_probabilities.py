#!/usr/bin/env python3
"""
Estimate probability of each justice ruling in favor of petitioner (Learning Resources)
in Learning Resources v. Trump, based on the justice position analysis.

Uses Claude Opus 4.5 to synthesize the per-argument analyses into overall probabilities.
"""

import json
import os
import sys
import time
from anthropic import Anthropic

# Get directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
    print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
    sys.exit(1)

# Initialize Anthropic client
client = Anthropic()

# Load the justice position analysis
with open(os.path.join(SCRIPT_DIR, 'justice_position_analysis.json'), 'r') as f:
    analysis_data = json.load(f)

# Load arguments.json for context
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    arguments_data = json.load(f)

SYSTEM_PROMPT = """You are a Supreme Court analyst with expertise in predicting justice voting behavior based on prior opinions and voting patterns.

Your task is to estimate the probability that each current Supreme Court justice will vote IN FAVOR OF THE PETITIONER (Learning Resources) in the case Learning Resources v. Trump.

## Case Overview
Learning Resources v. Trump challenges President Trump's use of IEEPA (International Emergency Economic Powers Act) to impose sweeping tariffs. The petitioner argues:
1. "Regulate importation" in IEEPA does not include tariff authority
2. The Major Questions Doctrine requires clear congressional authorization for such vast economic power
3. No president has ever used IEEPA for tariffs in its 50-year history
4. The statutory context (surrounding verbs) confirms no revenue-raising intent

The respondent (government) argues:
1. "Regulate" historically includes tariffs as a method of regulating commerce
2. Congress ratified this interpretation when enacting IEEPA after Yoshida
3. The Major Questions Doctrine doesn't apply in foreign affairs
4. Presidential foreign affairs deference applies

## Probability Scale
- 0-15%: Almost certainly votes for government
- 16-35%: Likely votes for government, but some uncertainty
- 36-50%: Leans government, could be persuaded
- 51-65%: Leans petitioner, could be persuaded
- 66-85%: Likely votes for petitioner
- 86-100%: Almost certainly votes for petitioner

## Output Format
For each justice, provide:

### [Justice Name]
**PROBABILITY FOR PETITIONER: [X]%**
**CONFIDENCE: [High/Medium/Low]**

**Key Factors Favoring Petitioner:**
- [Factor 1]
- [Factor 2]

**Key Factors Favoring Government:**
- [Factor 1]
- [Factor 2]

**Critical Uncertainty:**
- [What could change this estimate]

**Reasoning:** [2-3 sentence synthesis]

---

After analyzing all 9 justices, provide:

## SUMMARY TABLE
| Justice | P(Petitioner) | Confidence | Key Driver |
|---------|---------------|------------|------------|
| Roberts | X% | H/M/L | [brief] |
| ... | | | |

## PREDICTED OUTCOME
- Expected votes for petitioner: [X.X]
- Most likely outcome: [X-X] for [petitioner/government]
- Key swing justices: [names]

## OVERALL CASE ASSESSMENT
[2-3 paragraphs on likely outcome and key uncertainties]
"""


def build_analysis_context():
    """Build the full context from all argument analyses."""

    context = """## JUSTICE POSITION ANALYSES BY ARGUMENT

Below are detailed analyses of how each justice has ruled in relevant precedent cases, organized by argument.

"""

    for analysis in analysis_data['analyses']:
        if analysis.get('skipped'):
            continue

        arg_id = analysis['argument_id']
        side = analysis.get('side', 'unknown').upper()
        summary = analysis.get('argument_summary', '')

        context += f"""
### {arg_id} ({side})
**Argument:** {summary}

{analysis['analysis']}

---
"""

    # Add summary of arguments
    context += """
## ARGUMENT SUMMARY

**Petitioner Arguments (Learning Resources):**
"""
    for arg in arguments_data['arguments']:
        if arg['side'] == 'petitioner':
            context += f"- {arg['argument_id']}: {arg['summary']}\n"

    context += """
**Respondent Arguments (Government):**
"""
    for arg in arguments_data['arguments']:
        if arg['side'] == 'respondent':
            context += f"- {arg['argument_id']}: {arg['summary']}\n"

    return context


def estimate_probabilities():
    """Send analysis to Claude for probability estimation."""

    context = build_analysis_context()

    user_message = f"""Based on the justice position analyses below, estimate the probability that each of the 9 current Supreme Court justices will vote IN FAVOR OF THE PETITIONER (Learning Resources) in Learning Resources v. Trump.

{context}

---

## YOUR TASK

For each of the 9 current justices (Roberts, Thomas, Alito, Sotomayor, Kagan, Gorsuch, Kavanaugh, Barrett, Jackson):

1. Synthesize their positions across all analyzed arguments
2. Weight factors by:
   - Recency (2020+ cases weighted more)
   - Opinion authorship (authored > joined)
   - Issue specificity (same legal issue > analogous)
   - Strength of language in opinions
3. Estimate probability of voting for petitioner (0-100%)
4. Assign confidence level (High/Medium/Low)
5. Identify the key driver of your estimate

Then provide:
- Summary table of all 9 justices
- Predicted case outcome
- Overall assessment

Be precise with your probability estimates. Avoid clustering everyone at 50%. Use the full range based on the evidence.
"""

    print("Sending to Claude Opus 4.5 for probability estimation...")
    print("(This may take a minute due to the large context...)")

    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return response.content[0].text, response.usage


def main():
    print("=" * 70)
    print("Justice Vote Probability Estimation: Learning Resources v. Trump")
    print("=" * 70)
    print()

    analysis, usage = estimate_probabilities()

    print(f"\nComplete ({usage.input_tokens:,} input tokens, {usage.output_tokens:,} output tokens)")

    # Save results
    results = {
        'metadata': {
            'description': 'Probability estimates for each justice voting for petitioner',
            'model': 'claude-opus-4-5-20251101',
            'created': time.strftime('%Y-%m-%d %H:%M:%S'),
            'input_tokens': usage.input_tokens,
            'output_tokens': usage.output_tokens,
        },
        'analysis': analysis
    }

    # Save JSON
    json_path = os.path.join(SCRIPT_DIR, 'justice_vote_probabilities.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved JSON to: {json_path}")

    # Save markdown
    md_path = os.path.join(SCRIPT_DIR, 'justice_vote_probabilities.md')
    with open(md_path, 'w') as f:
        f.write("# Justice Vote Probability Estimation\n")
        f.write("## Learning Resources v. Trump\n\n")
        f.write(f"Generated: {results['metadata']['created']}\n")
        f.write(f"Model: {results['metadata']['model']}\n\n")
        f.write("---\n\n")
        f.write(analysis)
    print(f"Saved Markdown to: {md_path}")

    # Print the analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70 + "\n")
    print(analysis)


if __name__ == "__main__":
    main()
