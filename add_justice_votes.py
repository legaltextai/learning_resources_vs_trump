#!/usr/bin/env python3
"""
Add justice voting records to each relevant_case in arguments.json.
For each case, shows how current justices voted when they participated.
"""

import json
import csv
import os

# Get directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Current justices with their Spaeth codes
CURRENT_JUSTICES = {
    111: {"name": "John G. Roberts Jr.", "position": "Chief Justice", "tenure_start": 2005},
    108: {"name": "Clarence Thomas", "position": "Associate Justice", "tenure_start": 1991},
    112: {"name": "Samuel A. Alito Jr.", "position": "Associate Justice", "tenure_start": 2006},
    113: {"name": "Sonia Sotomayor", "position": "Associate Justice", "tenure_start": 2009},
    114: {"name": "Elena Kagan", "position": "Associate Justice", "tenure_start": 2010},
    115: {"name": "Neil M. Gorsuch", "position": "Associate Justice", "tenure_start": 2017},
    116: {"name": "Brett M. Kavanaugh", "position": "Associate Justice", "tenure_start": 2018},
    117: {"name": "Amy Coney Barrett", "position": "Associate Justice", "tenure_start": 2020},
    118: {"name": "Ketanji Brown Jackson", "position": "Associate Justice", "tenure_start": 2022},
}

# Vote code mappings
VOTE_MAP = {
    1: "majority",
    2: "dissent",
    3: "concurrence",
    4: "special_concurrence",
    5: "judgment",
    6: "dissent_cert_denial",
    7: "jurisdictional_dissent",
    8: "no_vote",
}

# Opinion code mappings
OPINION_MAP = {
    1: "author",
    2: "concurring",
    3: "dissenting",
    4: "concur_dissent",
    5: "special_concur_dissent",
    6: "none",
}

# Direction code mappings
DIRECTION_MAP = {
    1: "conservative",
    2: "liberal",
    3: "unspecifiable",
}

# Load arguments.json
print("Loading arguments.json...")
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    data = json.load(f)

# Collect all unique case_ids from relevant_cases
all_case_ids = set()
for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        all_case_ids.add(case['case_id'])

print(f"Found {len(all_case_ids)} unique case_ids to look up")

# Load justice-centered dataset and index by caseId
print("Loading justice-centered Spaeth database...")
justice_votes_by_case = {}

with open(os.path.join(SCRIPT_DIR, 'spaeth', 'SCDB_2025_01_justiceCentered_LegalProvision.csv'), 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        case_id = row['caseId']
        justice_id = int(row['justice']) if row['justice'] else None

        # Only track current justices
        if justice_id not in CURRENT_JUSTICES:
            continue

        if case_id not in justice_votes_by_case:
            justice_votes_by_case[case_id] = []

        # Avoid duplicate entries for same justice in same case
        if any(v['justice_id'] == justice_id for v in justice_votes_by_case[case_id]):
            continue

        vote_code = int(row['vote']) if row['vote'] else None
        opinion_code = int(row['opinion']) if row['opinion'] else None
        direction_code = int(row['direction']) if row['direction'] else None

        justice_votes_by_case[case_id].append({
            'justice_id': justice_id,
            'justice_name': CURRENT_JUSTICES[justice_id]['name'],
            'vote': VOTE_MAP.get(vote_code, 'unknown'),
            'opinion': OPINION_MAP.get(opinion_code, 'unknown'),
        })

print(f"Indexed {len(justice_votes_by_case)} cases with current justice votes")

# Mapping of custom case IDs in arguments.json to Spaeth case IDs
CASE_ID_MAP = {
    "Trump-Hawaii": "2017-074",   # TRUMP v. HAWAII (2018)
    "Yates": "2014-015",          # YATES v. UNITED STATES (2015) - fish destruction case
    "Cochise": "2018-058",        # COCHISE CONSULTANCY v. U.S. (2019)
    "Dalton": "1993-050",         # DALTON v. SPECTER (1994)
}

# Cases not in Spaeth (non-SCOTUS or too old for any current justice)
NON_SPAETH_CASES = {
    "Yoshida": "Federal Circuit case (CCPA 1975), not in SCOTUS database",
    "Gibbons": "Pre-modern era case (1824), predates current justices",
    "McGoldrick": "Pre-modern era case (1940), predates current justices",
    "Board-Trustees": "Pre-modern era case (1933), predates current justices",
    "Curtiss-Wright": "Pre-modern era case (1936), predates current justices",
    "NFIB-OSHA": "Emergency application (2022), may not be in standard Spaeth database",
}

# Update arguments.json with justice votes
cases_updated = 0
cases_no_votes = 0

for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        case_id = case['case_id']

        # Map custom IDs to Spaeth IDs
        spaeth_id = CASE_ID_MAP.get(case_id, case_id)

        if spaeth_id in justice_votes_by_case:
            # Sort by justice_id for consistent ordering
            votes = sorted(justice_votes_by_case[spaeth_id], key=lambda x: x['justice_id'])
            case['justice_votes'] = votes
            cases_updated += 1
        else:
            case['justice_votes'] = []
            # Add note explaining why no votes
            if case_id in NON_SPAETH_CASES:
                case['justice_votes_note'] = NON_SPAETH_CASES[case_id]
            elif case.get('year') and case['year'] < 1991:
                case['justice_votes_note'] = f"Case from {case['year']} predates all current justices"
            elif case.get('year') and case['year'] < 2005:
                case['justice_votes_note'] = f"Case from {case['year']} predates most current justices (only Thomas served)"
            else:
                case['justice_votes_note'] = "Case not found in Spaeth SCOTUS database"
            cases_no_votes += 1

# Write updated JSON
print(f"\nWriting updated arguments.json...")
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n=== Summary ===")
print(f"Cases with justice votes: {cases_updated}")
print(f"Cases without votes: {cases_no_votes}")

# Print details of cases with current justice participation
print("\n=== Cases with Current Justice Votes ===")
for case_id in sorted(all_case_ids):
    spaeth_id = CASE_ID_MAP.get(case_id, case_id)
    if spaeth_id in justice_votes_by_case:
        votes = justice_votes_by_case[spaeth_id]
        # Get last name only (handle "Jr." properly)
        def get_last_name(name):
            parts = name.replace(" Jr.", "").replace(" Sr.", "").split()
            return parts[-1] if parts else name
        vote_summary = ", ".join([f"{get_last_name(v['justice_name'])}:{v['vote'][:3]}" for v in votes])
        print(f"  {case_id}: {len(votes)} justices - {vote_summary}")

print("\n=== Cases Without Current Justice Votes ===")
# Get year lookup from data
year_by_case = {}
for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        year_by_case[case['case_id']] = case.get('year')

for case_id in sorted(all_case_ids):
    spaeth_id = CASE_ID_MAP.get(case_id, case_id)
    if spaeth_id not in justice_votes_by_case:
        year = year_by_case.get(case_id)
        if case_id in NON_SPAETH_CASES:
            reason = NON_SPAETH_CASES[case_id]
        elif year and year < 1991:
            reason = f"Case from {year} predates all current justices (Thomas joined 1991)"
        elif year and year < 2005:
            reason = f"Case from {year} - only Thomas served (Roberts joined 2005)"
        else:
            reason = "Case not found in Spaeth SCOTUS database"
        print(f"  {case_id}: {reason}")
