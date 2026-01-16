#!/usr/bin/env python3
"""
Extract opinion text from CourtListener for all cases in arguments.json.
Creates a separate case_opinions.json dataset linked by case_id.

Workflow:
1. Search CourtListener by case name + citation
2. Get cluster_id from first search result
3. Fetch opinions from opinions endpoint using cluster_id
4. Extract text from first available text field
"""

import json
import os
import requests
import time
import re
import sys
import urllib.parse

# Get directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for API key
api_key = os.environ.get('COURTLISTENER_API_KEY')
if not api_key:
    print("ERROR: COURTLISTENER_API_KEY environment variable not set.")
    print("Please set it with: export COURTLISTENER_API_KEY='your-key-here'")
    print("Get a free API key at: https://www.courtlistener.com/help/api/rest/")
    sys.exit(1)

HEADERS = {"Authorization": f"Token {api_key}"}

# Load arguments.json
print("Loading arguments.json...")
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    data = json.load(f)

# Collect all unique cases
all_cases = {}
for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        case_id = case['case_id']
        if case_id not in all_cases:
            all_cases[case_id] = {
                'case_id': case_id,
                'case_name': case['case_name'],
                'citation': case['citation'],
                'year': case.get('year'),
                'url': case.get('url', ''),
            }

print(f"Found {len(all_cases)} unique cases")

# Manual overrides for cases where search doesn't return correct result
MANUAL_CLUSTER_IDS = {
    "2023-015": 9986254,   # Loper Bright Enterprises v. Raimondo - SCOTUS 2024
    "2021-045": 6623243,   # West Virginia v. EPA - SCOTUS 2022
}


def normalize_case_name(name):
    """Normalize case name for comparison."""
    # Remove common prefixes/suffixes and lowercase
    name = name.lower()
    for term in ['et al.', 'et al', 'inc.', 'inc', 'llc', 'corp.', 'corp', 'v.', 'v ']:
        name = name.replace(term, ' ')
    # Keep only alphanumeric and spaces
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return ' '.join(name.split())


def case_names_match(expected, actual):
    """Check if case names match (allowing for variations)."""
    exp_norm = normalize_case_name(expected)
    act_norm = normalize_case_name(actual)

    # Get key words from each (first few significant words)
    exp_words = [w for w in exp_norm.split() if len(w) > 2][:3]
    act_words = [w for w in act_norm.split() if len(w) > 2][:3]

    # Check if at least 2 key words match
    matches = sum(1 for w in exp_words if w in act_words)
    return matches >= 2 or exp_words[0] in act_words if exp_words else False


def search_case(case_name, citation):
    """Search CourtListener by case name + citation, return cluster_id and URL."""
    query = f"{case_name}, {citation}"
    url = "https://www.courtlistener.com/api/rest/v4/search/"
    params = {"q": query}

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            results = resp.json().get('results', [])
            # Find the first result that actually matches the case name
            for result in results[:10]:  # Check up to 10 results
                result_name = result.get('caseName', '')
                if case_names_match(case_name, result_name):
                    cluster_id = result.get('cluster_id')
                    abs_url = result.get('absolute_url', '')
                    full_url = f"https://www.courtlistener.com{abs_url}" if abs_url else None
                    return cluster_id, full_url
            # If no match found, log and return None
            if results:
                print(f"    No matching case found in {len(results)} results")
                print(f"    First result was: {results[0].get('caseName', 'unknown')}")
        return None, None
    except Exception as e:
        print(f"    Search error: {e}")
        return None, None


def get_opinion_text(cluster_id):
    """Fetch opinion text from CourtListener API using cluster_id.

    Returns the first available text field from:
    plain_text, html_with_citations, html, html_lawbox, html_columbia, html_anon_2020, xml_harvard
    """
    url = f"https://www.courtlistener.com/api/rest/v4/opinions/"
    params = {"cluster": cluster_id}

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            results = resp.json().get('results', [])
            if results:
                # Sort by type to prefer combined/majority opinions
                opinions = sorted(results, key=lambda x: x.get('type', 'zzz'))

                for opinion in opinions:
                    # Try text fields in order of preference
                    for field in ['plain_text', 'html_with_citations', 'html', 'html_lawbox',
                                  'html_columbia', 'html_anon_2020', 'xml_harvard']:
                        text = opinion.get(field, '')
                        if text and len(text.strip()) > 100:
                            return {
                                'opinion_id': opinion.get('id'),
                                'opinion_type': opinion.get('type'),
                                'text_source': field,
                                'text': text,
                                'author_str': opinion.get('author_str', ''),
                                'per_curiam': opinion.get('per_curiam', False),
                                'page_count': opinion.get('page_count'),
                            }

                # If no substantial text, return metadata
                if opinions:
                    return {
                        'opinion_id': opinions[0].get('id'),
                        'opinion_type': opinions[0].get('type'),
                        'text_source': None,
                        'text': None,
                        'note': 'No text available in API response',
                    }
        return None
    except Exception as e:
        print(f"    Opinion fetch error: {e}")
        return None


# Build the opinions dataset
case_opinions = {
    'metadata': {
        'description': 'Opinion text for cases referenced in Learning Resources v. Trump arguments',
        'source': 'CourtListener API',
        'created': time.strftime('%Y-%m-%d'),
        'linked_to': 'arguments.json via case_id',
    },
    'cases': []
}

# Process each case
for case_id, case_info in all_cases.items():
    print(f"\nProcessing: {case_id} - {case_info['case_name'][:50]}...")

    case_entry = {
        'case_id': case_id,
        'case_name': case_info['case_name'],
        'citation': case_info['citation'],
        'year': case_info['year'],
    }

    # Step 1: Check manual overrides first, then search
    if case_id in MANUAL_CLUSTER_IDS:
        cluster_id = MANUAL_CLUSTER_IDS[case_id]
        courtlistener_url = f"https://www.courtlistener.com/opinion/{cluster_id}/"
        print(f"  Using manual override: cluster {cluster_id}")
    else:
        print(f"  Searching: {case_info['case_name'][:40]}, {case_info['citation']}")
        cluster_id, courtlistener_url = search_case(case_info['case_name'], case_info['citation'])

    if cluster_id:
        case_entry['cluster_id'] = cluster_id
        case_entry['courtlistener_url'] = courtlistener_url
        print(f"  Found cluster: {cluster_id}")

        # Step 2: Fetch opinion text
        opinion_data = get_opinion_text(cluster_id)

        if opinion_data:
            case_entry['opinion_id'] = opinion_data.get('opinion_id')
            case_entry['opinion_type'] = opinion_data.get('opinion_type')
            case_entry['text_source'] = opinion_data.get('text_source')
            case_entry['author'] = opinion_data.get('author_str')
            case_entry['per_curiam'] = opinion_data.get('per_curiam')
            case_entry['page_count'] = opinion_data.get('page_count')

            if opinion_data.get('text'):
                case_entry['text'] = opinion_data['text']
                text_len = len(opinion_data['text'])
                print(f"  Got text ({opinion_data['text_source']}): {text_len:,} chars")
            else:
                case_entry['text'] = None
                case_entry['note'] = opinion_data.get('note', 'No text available')
                print(f"  No text available")
        else:
            case_entry['note'] = 'Failed to fetch opinion from API'
            print(f"  Failed to fetch opinion")
    else:
        case_entry['cluster_id'] = None
        case_entry['courtlistener_url'] = case_info.get('url')
        case_entry['note'] = 'Case not found in CourtListener search'
        print(f"  Not found in search")

    case_opinions['cases'].append(case_entry)
    time.sleep(0.5)  # Rate limiting

# Write the dataset
output_path = os.path.join(SCRIPT_DIR, 'case_opinions.json')
print(f"\n\nWriting to {output_path}...")
with open(output_path, 'w') as f:
    json.dump(case_opinions, f, indent=2)

# Summary
cases_with_text = sum(1 for c in case_opinions['cases'] if c.get('text'))
cases_without = len(case_opinions['cases']) - cases_with_text

print(f"\n=== Summary ===")
print(f"Total cases: {len(case_opinions['cases'])}")
print(f"Cases with text: {cases_with_text}")
print(f"Cases without text: {cases_without}")

if cases_without > 0:
    print("\n=== Cases without text ===")
    for case in case_opinions['cases']:
        if not case.get('text'):
            print(f"  {case['case_id']}: {case.get('note', 'Unknown reason')}")
