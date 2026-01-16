#!/usr/bin/env python3
"""
Add relevant_cases array to each argument in arguments.json
based on Spaeth database queries and cases cited in briefs.
"""

import json
import csv
import os
from collections import defaultdict

# Get directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load arguments.json
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    data = json.load(f)

# Load Spaeth database
spaeth_cases = []
with open(os.path.join(SCRIPT_DIR, 'spaeth', 'SCDB_2025_01_caseCentered_LegalProvision.csv'), 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        spaeth_cases.append(row)

# Build index by case ID to avoid duplicates
case_by_id = {}
for case in spaeth_cases:
    case_id = case['caseId']
    if case_id not in case_by_id:
        case_by_id[case_id] = case

# Key cases from Spaeth database organized by relevance to arguments
# These are cases found in the database that are relevant to IEEPA/tariff issues

LANDMARK_CASES = {
    # Executive authority cases (issue 130015)
    "2013-069": {
        "relevance": "NLRB appointments; executive authority vis-a-vis Congress",
        "arguments": ["ARG-R04", "ARG-R07"]
    },
    "2014-011": {
        "relevance": "Zivotofsky - President's foreign affairs recognition power",
        "arguments": ["ARG-R04", "ARG-R07", "ARG-R09"]
    },
    "2019-071": {
        "relevance": "SEILA LAW - CFPB structure; removal power limits",
        "arguments": ["ARG-P05", "ARG-R04"]
    },
    "2019-074": {
        "relevance": "Trump v. Mazars - congressional oversight of President",
        "arguments": ["ARG-P05", "ARG-R04"]
    },
    "2020-029": {
        "relevance": "Collins v. Yellen - FHFA structure; executive authority",
        "arguments": ["ARG-R04", "ARG-R07"]
    },
    "2020-044": {
        "relevance": "Arthrex - appointments clause; executive control",
        "arguments": ["ARG-R04", "ARG-R07"]
    },

    # Youngstown - seminal executive power case
    "1951-088": {
        "relevance": "Youngstown - steel seizure; Jackson's three-zone framework for presidential power",
        "arguments": ["ARG-R04", "ARG-R07", "ARG-P05"]
    },

    # IEEPA/TWEA related
    "1980-152": {
        "relevance": "Dames & Moore - IEEPA hostage claims; presidential emergency powers",
        "arguments": ["ARG-R02", "ARG-R04", "ARG-R07", "ARG-R09", "ARG-P03", "ARG-P07"]
    },

    # Algonquin - key precedent on 'adjust imports'
    "1975-133": {
        "relevance": "Algonquin - 'adjust imports' includes license fees; monetary methods",
        "arguments": ["ARG-R01", "ARG-R03", "ARG-R06", "ARG-P01"]
    },

    # Zemel - foreign affairs delegation
    "1964-095": {
        "relevance": "Zemel - passport restrictions; broad delegation in foreign affairs",
        "arguments": ["ARG-R04", "ARG-R07"]
    },

    # Major questions doctrine
    "2021-045": {
        "relevance": "West Virginia v. EPA - major questions doctrine; generation shifting rule",
        "arguments": ["ARG-P05", "ARG-R04"]
    },
    "2022-038": {
        "relevance": "Biden v. Nebraska - student loan forgiveness; major questions doctrine",
        "arguments": ["ARG-P05", "ARG-R04"]
    },
    "2023-015": {
        "relevance": "Loper Bright - overruled Chevron; statutory interpretation",
        "arguments": ["ARG-P01", "ARG-P03", "ARG-R01", "ARG-R02"]
    },

    # Nondelegation
    "2018-003": {
        "relevance": "Gundy - SORNA delegation; nondelegation doctrine standards",
        "arguments": ["ARG-P05", "ARG-R07"]
    },
    "1983-134": {
        "relevance": "Chevron - agency deference (overruled by Loper Bright)",
        "arguments": ["ARG-P01", "ARG-R01"]
    },

    # K Mart - jurisdiction
    "1987-043": {
        "relevance": "K Mart v. Cartier - gray market goods; district court jurisdiction",
        "arguments": ["ARG-P08", "ARG-R08"]
    },

    # Commerce power
    "2002-079": {
        "relevance": "American Insurance Assn v. Garamendi - executive agreements; foreign affairs preemption",
        "arguments": ["ARG-R04", "ARG-R07", "ARG-R09"]
    },

    # Free Enterprise Fund - executive power
    "2009-088": {
        "relevance": "Free Enterprise Fund - PCAOB removal; executive authority",
        "arguments": ["ARG-R04", "ARG-R07"]
    },

    # Morrison - executive power
    "1987-149": {
        "relevance": "Morrison v. Olson - independent counsel; executive power limits",
        "arguments": ["ARG-R04", "ARG-R07"]
    },
}

# Cases cited in briefs that aren't in Spaeth but should be noted
BRIEF_CITED_CASES = {
    # Yoshida - key TWEA tariff precedent (Federal Circuit, not Supreme Court)
    "Yoshida": {
        "case_name": "United States v. Yoshida Int'l, Inc.",
        "citation": "526 F.2d 560 (C.C.P.A. 1975)",
        "year": 1975,
        "relevance": "Nixon tariffs under TWEA upheld; 'regulate importation' includes tariffs",
        "arguments": ["ARG-R02", "ARG-R10", "ARG-P03", "ARG-P07"]
    },
    # Regan v. Wald
    "1983-125": {
        "case_name": "Regan v. Wald",
        "citation": "468 U.S. 222 (1984)",
        "year": 1984,
        "relevance": "IEEPA authorities 'essentially the same as' TWEA",
        "arguments": ["ARG-R02", "ARG-P07"]
    },
    # Curtiss-Wright
    "Curtiss-Wright": {
        "case_name": "United States v. Curtiss-Wright Export Corp.",
        "citation": "299 U.S. 304 (1936)",
        "year": 1936,
        "relevance": "President's plenary foreign affairs power; broad delegation permitted",
        "arguments": ["ARG-R04", "ARG-R07", "ARG-R09"]
    },
    # Gibbons v. Ogden
    "Gibbons": {
        "case_name": "Gibbons v. Ogden",
        "citation": "22 U.S. (9 Wheat.) 1 (1824)",
        "year": 1824,
        "relevance": "Commerce power scope; regulation vs taxation distinction",
        "arguments": ["ARG-P01", "ARG-R01"]
    },
    # McGoldrick
    "McGoldrick": {
        "case_name": "McGoldrick v. Gulf Oil Corp.",
        "citation": "309 U.S. 414 (1940)",
        "year": 1940,
        "relevance": "Laying duty on imports is exercise of commerce power",
        "arguments": ["ARG-R01", "ARG-R05"]
    },
    # Board of Trustees
    "Board-Trustees": {
        "case_name": "Board of Trustees v. United States",
        "citation": "289 U.S. 48 (1933)",
        "year": 1933,
        "relevance": "Tariffs may be imposed under commerce power, not just taxing power",
        "arguments": ["ARG-R05", "ARG-P02"]
    },
    # Trump v. Hawaii
    "Trump-Hawaii": {
        "case_name": "Trump v. Hawaii",
        "citation": "585 U.S. 667 (2018)",
        "year": 2018,
        "relevance": "Deference to executive in immigration/national security context",
        "arguments": ["ARG-R09", "ARG-R04"]
    },
    # Dalton v. Specter
    "Dalton": {
        "case_name": "Dalton v. Specter",
        "citation": "511 U.S. 462 (1994)",
        "year": 1994,
        "relevance": "Executive determinations not subject to judicial review",
        "arguments": ["ARG-R09"]
    },
    # NFIB v. OSHA
    "NFIB-OSHA": {
        "case_name": "NFIB v. OSHA",
        "citation": "595 U.S. 109 (2022)",
        "year": 2022,
        "relevance": "Vaccine mandate stayed; major questions doctrine application",
        "arguments": ["ARG-P05"]
    },
    # Cochise Consultancy
    "Cochise": {
        "case_name": "Cochise Consultancy, Inc. v. United States ex rel. Hunt",
        "citation": "587 U.S. 262 (2019)",
        "year": 2019,
        "relevance": "Single statutory phrase must have consistent meaning",
        "arguments": ["ARG-P02"]
    },
    # Yates v. United States
    "Yates": {
        "case_name": "Yates v. United States",
        "citation": "574 U.S. 528 (2015)",
        "year": 2015,
        "relevance": "Noscitur a sociis - word known by company it keeps",
        "arguments": ["ARG-P04"]
    },
}

def get_case_info(case_id):
    """Get case info from Spaeth database"""
    if case_id in case_by_id:
        case = case_by_id[case_id]
        return {
            "case_id": case_id,
            "case_name": case['caseName'].strip('"'),
            "citation": case['usCite'].strip('"') if case['usCite'] else case['sctCite'].strip('"'),
            "year": int(case['term']) + 1 if case['term'] else None
        }
    return None

# Build mapping of argument_id -> relevant_cases
argument_cases = defaultdict(list)

# Add cases from Spaeth database
for case_id, info in LANDMARK_CASES.items():
    case_info = get_case_info(case_id)
    if case_info:
        case_info['relevance'] = info['relevance']
        for arg_id in info['arguments']:
            # Check if case already added
            if not any(c['case_id'] == case_id for c in argument_cases[arg_id]):
                argument_cases[arg_id].append(case_info.copy())

# Add cases cited in briefs (may not be in Spaeth)
for case_key, info in BRIEF_CITED_CASES.items():
    case_entry = {
        "case_id": case_key,
        "case_name": info['case_name'],
        "citation": info['citation'],
        "year": info['year'],
        "relevance": info['relevance']
    }
    for arg_id in info['arguments']:
        # Check if case already added
        if not any(c['case_id'] == case_key for c in argument_cases[arg_id]):
            argument_cases[arg_id].append(case_entry.copy())

# Sort cases by year for each argument
for arg_id in argument_cases:
    argument_cases[arg_id].sort(key=lambda x: x['year'] if x['year'] else 0)

# Add relevant_cases to each argument in the JSON
for argument in data['arguments']:
    arg_id = argument['argument_id']
    if arg_id in argument_cases:
        argument['relevant_cases'] = argument_cases[arg_id]
    else:
        argument['relevant_cases'] = []

# Write updated JSON
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'w') as f:
    json.dump(data, f, indent=2)

# Print summary
print("Added relevant_cases to arguments:")
for arg_id, cases in sorted(argument_cases.items()):
    print(f"  {arg_id}: {len(cases)} cases")

print(f"\nTotal unique cases added: {len(set(c['case_id'] for cases in argument_cases.values() for c in cases))}")
