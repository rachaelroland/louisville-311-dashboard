#!/usr/bin/env python3
"""
NSR (Non-Service Request) Deep Dive Analysis
The NSR categories account for ~45% of call center volume - let's understand what they are
"""

import pandas as pd
import json
from collections import Counter

# File paths
PROCESSED_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv"
RAW_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv"

print("=" * 80)
print("NSR (NON-SERVICE REQUEST) DEEP DIVE ANALYSIS")
print("=" * 80)
print()

# Load data
processed_df = pd.read_csv(PROCESSED_CSV)
raw_df = pd.read_csv(RAW_CSV, encoding='utf-8')

# Join datasets
merged_df = processed_df.merge(
    raw_df[['service_request_id', 'source']],
    on='service_request_id',
    how='left'
)

# Filter Call Center requests
call_center_df = merged_df[merged_df['source'].str.strip().str.upper() == 'CALL CENTER'].copy()

# Filter NSR categories
nsr_df = call_center_df[call_center_df['service_name'].str.contains('NSR', na=False)].copy()

print(f"Total NSR call center requests: {len(nsr_df):,}")
print(f"Percentage of call center volume: {len(nsr_df)/len(call_center_df)*100:.1f}%")
print()

# NSR category breakdown
print("=" * 80)
print("NSR CATEGORY BREAKDOWN")
print("=" * 80)
print()

nsr_categories = nsr_df['service_name'].value_counts()
for idx, (category, count) in enumerate(nsr_categories.items(), 1):
    pct = count / len(nsr_df) * 100
    print(f"{idx}. {category:40s} {count:7,} ({pct:5.1f}%)")
print()

# Analyze descriptions to understand what NSR Metro Agencies actually means
print("=" * 80)
print("NSR METRO AGENCIES - SAMPLE DESCRIPTIONS")
print("=" * 80)
print()

nsr_metro = nsr_df[nsr_df['service_name'] == 'NSR Metro Agencies']
print(f"Total NSR Metro Agencies: {len(nsr_metro):,}")
print()

# Get sample of non-empty descriptions
nsr_metro_with_desc = nsr_metro[
    nsr_metro['description'].notna() &
    (nsr_metro['description'].str.len() > 10)
].copy()

print(f"Records with descriptions: {len(nsr_metro_with_desc):,} ({len(nsr_metro_with_desc)/len(nsr_metro)*100:.1f}%)")
print()

# Sample descriptions
if len(nsr_metro_with_desc) > 0:
    print("Sample descriptions (first 20):")
    for idx, row in nsr_metro_with_desc.head(20).iterrows():
        desc = row['description'][:150]
        print(f"\n{idx+1}. {desc}")
print()

# Analyze topics for NSR categories
print("=" * 80)
print("TOPIC ANALYSIS FOR NSR CATEGORIES")
print("=" * 80)
print()

for nsr_category in nsr_categories.index[:6]:  # Top 6 NSR categories
    print(f"\n{nsr_category}")
    print("-" * 80)

    nsr_cat_df = nsr_df[nsr_df['service_name'] == nsr_category]

    # Aggregate topics
    topic_counter = Counter()
    for idx, row in nsr_cat_df.iterrows():
        if pd.notna(row['topics_json']) and row['topics_json'] != '':
            try:
                topics = json.loads(row['topics_json'])
                for topic in topics.keys():
                    topic_counter[topic] += 1
            except json.JSONDecodeError:
                pass

    if topic_counter:
        print(f"Top 10 topics:")
        for idx, (topic, count) in enumerate(topic_counter.most_common(10), 1):
            pct = count / len(nsr_cat_df) * 100
            print(f"  {idx:2d}. {topic:40s} {count:5,} ({pct:5.1f}%)")
    else:
        print("  No topic data available")

print()

# Agency responsible for NSR
print("=" * 80)
print("AGENCIES HANDLING NSR REQUESTS")
print("=" * 80)
print()

for nsr_category in nsr_categories.index[:6]:
    print(f"\n{nsr_category}")
    print("-" * 80)

    nsr_cat_df = nsr_df[nsr_df['service_name'] == nsr_category]
    agencies = nsr_cat_df['agency_responsible'].value_counts()

    print(f"Top agencies:")
    for idx, (agency, count) in enumerate(agencies.head(10).items(), 1):
        pct = count / len(nsr_cat_df) * 100
        agency_str = str(agency) if pd.notna(agency) else "BLANK/UNASSIGNED"
        print(f"  {idx:2d}. {agency_str:45s} {count:5,} ({pct:5.1f}%)")

print()

# Check urgency and sentiment for NSR categories
print("=" * 80)
print("NSR URGENCY & SENTIMENT PATTERNS")
print("=" * 80)
print()

for nsr_category in nsr_categories.index[:6]:
    print(f"\n{nsr_category}")
    print("-" * 80)

    nsr_cat_df = nsr_df[nsr_df['service_name'] == nsr_category]

    # Urgency
    urgency_counts = nsr_cat_df['urgency_level'].value_counts()
    print("Urgency:")
    for urgency in ['high', 'medium', 'low']:
        count = urgency_counts.get(urgency, 0)
        pct = count / len(nsr_cat_df) * 100
        print(f"  {urgency:6s}: {count:6,} ({pct:5.1f}%)")

    # Sentiment
    sentiment_counts = nsr_cat_df['sentiment'].value_counts()
    print("\nSentiment:")
    for sentiment in ['negative', 'neutral', 'positive']:
        count = sentiment_counts.get(sentiment, 0)
        pct = count / len(nsr_cat_df) * 100
        print(f"  {sentiment:8s}: {count:6,} ({pct:5.1f}%)")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
