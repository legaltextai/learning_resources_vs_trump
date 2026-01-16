#!/usr/bin/env python3
"""
Add case URLs to each relevant_cases entry in arguments.json
using CourtListener API.
"""

import json
import os
import requests
import sys
import time
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
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'r') as f:
    data = json.load(f)

# Collect all unique cases
all_cases = {}
for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        case_id = case['case_id']
        if case_id not in all_cases:
            all_cases[case_id] = case

print(f"Found {len(all_cases)} unique cases to look up")

# Map case_id to URL
case_urls = {}

def search_case(case_name, citation):
    """Search CourtListener by case name + citation, get cluster ID, then opinion URL"""
    # Build search query
    query = f"{case_name}, {citation}"

    url = "https://www.courtlistener.com/api/rest/v4/search/"
    params = {"q": query}

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            results = resp.json()
            if results.get('results') and len(results['results']) > 0:
                first_result = results['results'][0]
                cluster_id = first_result.get('cluster_id')
                absolute_url = first_result.get('absolute_url')

                if absolute_url:
                    return f"https://www.courtlistener.com{absolute_url}"
                elif cluster_id:
                    # Get opinion from cluster
                    opinion_url = f"https://www.courtlistener.com/api/rest/v4/opinions/?cluster={cluster_id}"
                    opinion_resp = requests.get(opinion_url, headers=HEADERS, timeout=30)
                    if opinion_resp.status_code == 200:
                        opinion_data = opinion_resp.json()
                        if opinion_data.get('results') and len(opinion_data['results']) > 0:
                            op_url = opinion_data['results'][0].get('absolute_url')
                            if op_url:
                                return f"https://www.courtlistener.com{op_url}"
                    # Fallback to cluster URL
                    return f"https://www.courtlistener.com/opinion/{cluster_id}/"
        else:
            print(f"    API returned status {resp.status_code}")
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None

# Look up each case
for case_id, case_info in all_cases.items():
    case_name = case_info['case_name']
    citation = case_info.get('citation', '')

    print(f"\nLooking up: {case_name[:60]}...")
    print(f"  Citation: {citation}")

    url = search_case(case_name, citation)

    if url:
        case_urls[case_id] = url
        print(f"  Found: {url}")
    else:
        # Try with just citation
        print(f"  Trying citation only...")
        url = search_case("", citation)
        if url:
            case_urls[case_id] = url
            print(f"  Found: {url}")
        else:
            print(f"  NOT FOUND")

    # Rate limiting
    time.sleep(0.5)

print(f"\n\nFound URLs for {len(case_urls)} of {len(all_cases)} cases")

# Update the JSON with URLs
for arg in data['arguments']:
    for case in arg.get('relevant_cases', []):
        case_id = case['case_id']
        if case_id in case_urls:
            case['url'] = case_urls[case_id]

# Write updated JSON
with open(os.path.join(SCRIPT_DIR, 'arguments.json'), 'w') as f:
    json.dump(data, f, indent=2)

print("\nUpdated arguments.json with case URLs")

# Print summary
print("\n=== URL Summary ===")
for case_id, url in sorted(case_urls.items()):
    print(f"{case_id}: {url}")

# Print missing cases
missing = set(all_cases.keys()) - set(case_urls.keys())
if missing:
    print(f"\n=== Missing Cases ({len(missing)}) ===")
    for case_id in missing:
        print(f"  {case_id}: {all_cases[case_id]['case_name'][:50]}")
