#!/usr/bin/env python3
"""
Analyze justice positions for each argument in Learning Resources v. Trump
using Claude Opus 4.5 as the analyst.

This script sends each argument along with its relevant cases and opinion text
to Claude for analysis following the Associate_instruction.md guidelines.
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

# Load the system prompt from Associate_instruction.md
with open(os.path.join(SCRIPT_DIR, 'Associate_instruction.md'), 'r') as f:
    SYSTEM_PROMPT = f.read()

# Load arguments.json
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    arguments_data = json.load(f)

# Load case_opinions.json (if available)
case_opinions_path = os.path.join(SCRIPT_DIR, 'case_opinions.json')
if os.path.exists(case_opinions_path):
    with open(case_opinions_path, 'r') as f:
        opinions_data = json.load(f)
    opinions_by_case = {c['case_id']: c for c in opinions_data['cases']}
else:
    print("Note: case_opinions.json not found. Run extract_opinions.py first to fetch opinion texts.")
    opinions_by_case = {}


def get_case_opinion_text(case_id, max_chars=50000):
    """Get opinion text for a case, truncated if necessary."""
    if case_id in opinions_by_case:
        text = opinions_by_case[case_id].get('text', '')
        if text and len(text) > max_chars:
            return text[:max_chars] + f"\n\n[... truncated, {len(text) - max_chars:,} more chars ...]"
        return text
    return None


def format_justice_votes(justice_votes):
    """Format justice votes for display."""
    if not justice_votes:
        return "No current justice participation"

    lines = []
    for jv in justice_votes:
        name = jv['justice_name']
        vote = jv['vote']
        opinion = jv['opinion']
        lines.append(f"  - {name}: {vote} ({opinion})")
    return "\n".join(lines)


def build_argument_context(argument):
    """Build the full context for analyzing an argument."""
    arg_id = argument['argument_id']
    side = argument['side']
    summary = argument['summary']
    detail = argument['detail']

    context = f"""
## ARGUMENT TO ANALYZE

**Argument ID:** {arg_id}
**Side:** {side.upper()}
**Summary:** {summary}

**Detail:** {detail}

---

## RELEVANT CASES WITH JUSTICE PARTICIPATION

"""

    relevant_cases = argument.get('relevant_cases', [])
    cases_with_votes = [c for c in relevant_cases if c.get('justice_votes')]
    cases_without_votes = [c for c in relevant_cases if not c.get('justice_votes')]

    if not cases_with_votes:
        context += "No cases with current justice participation for this argument.\n"
        return context, False

    for case in cases_with_votes:
        case_id = case['case_id']
        case_name = case['case_name']
        citation = case['citation']
        year = case.get('year', 'Unknown')
        relevance = case.get('relevance', 'Not specified')
        justice_votes = case.get('justice_votes', [])

        context += f"""
### {case_name} ({year})
**Citation:** {citation}
**Case ID:** {case_id}
**Relevance to Argument:** {relevance}

**Justice Votes:**
{format_justice_votes(justice_votes)}

"""
        # Add opinion text (truncated for very long opinions)
        opinion_text = get_case_opinion_text(case_id, max_chars=30000)
        if opinion_text:
            context += f"""**Opinion Text:**
<opinion case_id="{case_id}">
{opinion_text}
</opinion>

"""
        else:
            context += "**Opinion Text:** Not available\n\n"

    # Note cases without current justice participation
    if cases_without_votes:
        context += "\n### Cases Without Current Justice Participation\n"
        for case in cases_without_votes:
            note = case.get('justice_votes_note', 'Predates current justices')
            context += f"- {case['case_name']} ({case.get('year', '?')}): {note}\n"

    return context, True


def analyze_argument(argument):
    """Send argument to Claude for analysis."""
    arg_id = argument['argument_id']

    context, has_cases = build_argument_context(argument)

    if not has_cases:
        return {
            'argument_id': arg_id,
            'analysis': "No cases with current justice participation available for analysis.",
            'skipped': True
        }

    user_message = f"""Please analyze the following argument and the justice positions expressed in the relevant cases.

{context}

---

## YOUR TASK

Following the instructions in the system prompt, please:

1. Review each case where current justices participated
2. For each justice, identify their position on the legal issues relevant to this argument
3. Note whether they authored an opinion, wrote a concurrence/dissent, or merely joined
4. Synthesize their overall tendency on this type of issue
5. Provide prediction notes about how they might view this specific argument

Format your response as specified in the instructions, with a section for each justice who participated in at least one relevant case.
"""

    print(f"  Sending to Claude Opus 4.5...")

    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    analysis = response.content[0].text

    return {
        'argument_id': arg_id,
        'argument_summary': argument['summary'],
        'side': argument['side'],
        'analysis': analysis,
        'skipped': False,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens
    }


def main():
    """Main function to analyze all arguments."""
    print("=" * 60)
    print("Justice Position Analysis for Learning Resources v. Trump")
    print("=" * 60)
    print()

    results = {
        'metadata': {
            'description': 'Claude Opus 4.5 analysis of justice positions on each argument',
            'model': 'claude-opus-4-5-20251101',
            'created': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source_files': ['arguments.json', 'case_opinions.json', 'Associate_instruction.md']
        },
        'analyses': []
    }

    arguments = arguments_data['arguments']
    total = len(arguments)

    for i, argument in enumerate(arguments, 1):
        arg_id = argument['argument_id']
        print(f"\n[{i}/{total}] Analyzing {arg_id}: {argument['summary'][:60]}...")

        try:
            analysis = analyze_argument(argument)
            results['analyses'].append(analysis)

            if analysis['skipped']:
                print(f"  Skipped (no cases with current justice participation)")
            else:
                print(f"  Complete ({analysis['input_tokens']} in, {analysis['output_tokens']} out)")

            # Rate limiting - be gentle with the API
            if not analysis['skipped']:
                time.sleep(2)

        except Exception as e:
            print(f"  ERROR: {e}")
            results['analyses'].append({
                'argument_id': arg_id,
                'error': str(e),
                'skipped': True
            })

    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'justice_position_analysis.json')
    print(f"\n\nSaving results to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Also save as markdown for easier reading
    md_output_path = os.path.join(SCRIPT_DIR, 'justice_position_analysis.md')
    print(f"Saving markdown version to {md_output_path}...")

    with open(md_output_path, 'w') as f:
        f.write("# Justice Position Analysis: Learning Resources v. Trump\n\n")
        f.write(f"Generated: {results['metadata']['created']}\n")
        f.write(f"Model: {results['metadata']['model']}\n\n")
        f.write("---\n\n")

        for analysis in results['analyses']:
            f.write(f"## {analysis['argument_id']}\n\n")
            if 'argument_summary' in analysis:
                f.write(f"**{analysis['side'].upper()}:** {analysis['argument_summary']}\n\n")
            if analysis.get('skipped'):
                f.write(f"*Skipped: {analysis.get('analysis', analysis.get('error', 'Unknown reason'))}*\n\n")
            else:
                f.write(analysis['analysis'])
                f.write("\n\n")
            f.write("---\n\n")

    # Summary
    completed = sum(1 for a in results['analyses'] if not a.get('skipped'))
    skipped = sum(1 for a in results['analyses'] if a.get('skipped'))
    total_in = sum(a.get('input_tokens', 0) for a in results['analyses'])
    total_out = sum(a.get('output_tokens', 0) for a in results['analyses'])

    print(f"\n{'=' * 60}")
    print("COMPLETE")
    print(f"{'=' * 60}")
    print(f"Arguments analyzed: {completed}")
    print(f"Arguments skipped: {skipped}")
    print(f"Total tokens: {total_in:,} input, {total_out:,} output")
    print(f"\nOutput files:")
    print(f"  - {output_path}")
    print(f"  - {md_output_path}")


if __name__ == "__main__":
    main()
