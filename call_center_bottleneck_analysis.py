#!/usr/bin/env python3
"""
Louisville Metro 311 Call Center Bottleneck Analysis
Analyzes processed NLP data to identify bottlenecks and opportunities for self-service
"""

import pandas as pd
import json
from collections import Counter, defaultdict
import re

# File paths
PROCESSED_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv"
RAW_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv"

print("=" * 80)
print("LOUISVILLE METRO 311 CALL CENTER BOTTLENECK ANALYSIS")
print("=" * 80)
print()

# Load data
print("Loading data...")
processed_df = pd.read_csv(PROCESSED_CSV)
raw_df = pd.read_csv(RAW_CSV, encoding='utf-8')

print(f"Processed records: {len(processed_df):,}")
print(f"Raw records: {len(raw_df):,}")
print()

# Join datasets on service_request_id
print("Joining datasets...")
merged_df = processed_df.merge(
    raw_df[['service_request_id', 'source']],
    on='service_request_id',
    how='left'
)
print(f"Merged records: {len(merged_df):,}")
print()

# ============================================================================
# TASK 1: INFER SOURCE FROM NER WHEN BLANK
# ============================================================================
print("=" * 80)
print("TASK 1: SOURCE INFERENCE FROM NER ENTITIES")
print("=" * 80)
print()

# Check blank source distribution
blank_source = merged_df['source'].isna() | (merged_df['source'] == '')
print(f"Records with blank source: {blank_source.sum():,} ({blank_source.sum()/len(merged_df)*100:.1f}%)")
print()

# Analyze NER entities for source clues
source_clues = {
    'email': 0,
    'phone': 0,
    'web': 0,
    'mobile': 0,
    'other': 0
}

blank_source_df = merged_df[blank_source].copy()

def extract_source_clues(ner_json_str):
    """Extract contact method clues from NER entities"""
    if pd.isna(ner_json_str) or ner_json_str == '':
        return None

    try:
        ner_data = json.loads(ner_json_str)
        entities = ner_data.get('entities', [])

        for entity in entities:
            entity_text = entity.get('entity', '').lower()
            entity_type = entity.get('type', '').lower()

            # Email patterns
            if '@' in entity_text or 'email' in entity_text:
                return 'email'

            # Phone patterns
            if entity_type in ['phone', 'phone_number'] or re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', entity_text):
                return 'phone'

            # Web/app patterns
            if any(word in entity_text for word in ['app', 'website', 'online', 'portal', 'web']):
                return 'web'

            # Mobile patterns
            if 'mobile' in entity_text or 'cell' in entity_text:
                return 'mobile'

    except json.JSONDecodeError:
        pass

    return None

# Apply source inference
inferred_sources = blank_source_df['ner_json'].apply(extract_source_clues)
inferred_count = inferred_sources.notna().sum()

print(f"Source clues found in NER for {inferred_count:,} blank records:")
if inferred_count > 0:
    for source_type, count in inferred_sources.value_counts().items():
        print(f"  - {source_type}: {count:,}")
print()

# ============================================================================
# TASK 2: CALL CENTER BOTTLENECK ANALYSIS
# ============================================================================
print("=" * 80)
print("TASK 2: CALL CENTER BOTTLENECK ANALYSIS")
print("=" * 80)
print()

# Filter Call Center requests
call_center_df = merged_df[merged_df['source'].str.strip().str.upper() == 'CALL CENTER'].copy()
print(f"Total Call Center requests: {len(call_center_df):,}")
print()

# 2.1: Most common topics/service types
print("-" * 80)
print("2.1 MOST COMMON SERVICE TYPES")
print("-" * 80)
print()

service_counts = call_center_df['service_name'].value_counts()
print(f"Top 20 Service Types:")
for idx, (service, count) in enumerate(service_counts.head(20).items(), 1):
    pct = count / len(call_center_df) * 100
    print(f"{idx:2d}. {service:40s} {count:6,} ({pct:5.1f}%)")
print()

# Analyze topics from JSON
print("Analyzing topic patterns from NLP...")
topic_counter = Counter()
topic_details = defaultdict(list)

for idx, row in call_center_df.iterrows():
    if pd.notna(row['topics_json']) and row['topics_json'] != '':
        try:
            topics = json.loads(row['topics_json'])
            for topic, data in topics.items():
                topic_counter[topic] += data.get('count', 1)
                topic_details[topic].append({
                    'service_name': row['service_name'],
                    'urgency': row['urgency_level'],
                    'sentiment': row['sentiment']
                })
        except json.JSONDecodeError:
            pass

print(f"\nTop 20 Topics from NLP:")
for idx, (topic, count) in enumerate(topic_counter.most_common(20), 1):
    print(f"{idx:2d}. {topic:50s} {count:6,}")
print()

# 2.2: Urgency Distribution
print("-" * 80)
print("2.2 URGENCY DISTRIBUTION")
print("-" * 80)
print()

urgency_counts = call_center_df['urgency_level'].value_counts()
print("Urgency Level Distribution:")
for urgency in ['high', 'medium', 'low']:
    count = urgency_counts.get(urgency, 0)
    pct = count / len(call_center_df) * 100 if len(call_center_df) > 0 else 0
    print(f"  {urgency.upper():6s}: {count:6,} ({pct:5.1f}%)")

# Count blanks/other
other_count = len(call_center_df) - urgency_counts.sum()
if other_count > 0:
    pct = other_count / len(call_center_df) * 100
    print(f"  BLANK/OTHER: {other_count:6,} ({pct:5.1f}%)")
print()

# High urgency details
high_urgency_df = call_center_df[call_center_df['urgency_level'] == 'high']
print(f"High Urgency Call Center Requests: {len(high_urgency_df):,}")
print("\nTop 10 High Urgency Service Types:")
for idx, (service, count) in enumerate(high_urgency_df['service_name'].value_counts().head(10).items(), 1):
    pct = count / len(high_urgency_df) * 100
    print(f"{idx:2d}. {service:40s} {count:5,} ({pct:5.1f}%)")
print()

# 2.3: Sentiment Distribution
print("-" * 80)
print("2.3 SENTIMENT DISTRIBUTION")
print("-" * 80)
print()

sentiment_counts = call_center_df['sentiment'].value_counts()
print("Sentiment Distribution:")
for sentiment in ['negative', 'neutral', 'positive']:
    count = sentiment_counts.get(sentiment, 0)
    pct = count / len(call_center_df) * 100 if len(call_center_df) > 0 else 0
    print(f"  {sentiment.upper():8s}: {count:6,} ({pct:5.1f}%)")

# Count blanks
blank_sentiment = call_center_df['sentiment'].isna() | (call_center_df['sentiment'] == '')
if blank_sentiment.sum() > 0:
    pct = blank_sentiment.sum() / len(call_center_df) * 100
    print(f"  BLANK:    {blank_sentiment.sum():6,} ({pct:5.1f}%)")
print()

# Negative sentiment details
negative_df = call_center_df[call_center_df['sentiment'] == 'negative']
print(f"Negative Sentiment Call Center Requests: {len(negative_df):,}")
print("\nTop 10 Negative Sentiment Service Types:")
for idx, (service, count) in enumerate(negative_df['service_name'].value_counts().head(10).items(), 1):
    pct = count / len(negative_df) * 100
    print(f"{idx:2d}. {service:40s} {count:5,} ({pct:5.1f}%)")
print()

# 2.4: Agency Volume
print("-" * 80)
print("2.4 AGENCIES HANDLING CALL CENTER VOLUME")
print("-" * 80)
print()

agency_counts = call_center_df['agency_responsible'].value_counts()
print(f"Top 15 Agencies by Call Center Volume:")
for idx, (agency, count) in enumerate(agency_counts.head(15).items(), 1):
    pct = count / len(call_center_df) * 100
    print(f"{idx:2d}. {agency:50s} {count:6,} ({pct:5.1f}%)")
print()

# 2.5: High Urgency + Negative Sentiment (Systemic Bottlenecks)
print("-" * 80)
print("2.5 SYSTEMIC BOTTLENECKS: HIGH URGENCY + NEGATIVE SENTIMENT")
print("-" * 80)
print()

bottleneck_df = call_center_df[
    (call_center_df['urgency_level'] == 'high') &
    (call_center_df['sentiment'] == 'negative')
]

print(f"High Urgency + Negative Sentiment: {len(bottleneck_df):,} requests")
print(f"Percentage of call center volume: {len(bottleneck_df)/len(call_center_df)*100:.1f}%")
print()

print("Top 15 Service Types with High Urgency + Negative Sentiment:")
for idx, (service, count) in enumerate(bottleneck_df['service_name'].value_counts().head(15).items(), 1):
    pct = count / len(bottleneck_df) * 100
    print(f"{idx:2d}. {service:40s} {count:5,} ({pct:5.1f}%)")
print()

print("Top 10 Agencies with High Urgency + Negative Sentiment:")
for idx, (agency, count) in enumerate(bottleneck_df['agency_responsible'].value_counts().head(10).items(), 1):
    pct = count / len(bottleneck_df) * 100
    print(f"{idx:2d}. {agency:50s} {count:5,} ({pct:5.1f}%)")
print()

# ============================================================================
# TASK 3: ACTIONABLE BOTTLENECK FINDINGS
# ============================================================================
print("=" * 80)
print("TASK 3: ACTIONABLE BOTTLENECK FINDINGS")
print("=" * 80)
print()

# Identify high-volume, low-urgency service types (prime candidates for self-service)
print("-" * 80)
print("PRIME CANDIDATES FOR SELF-SERVICE (High Volume, Low/Medium Urgency)")
print("-" * 80)
print()

low_med_urgency_df = call_center_df[
    call_center_df['urgency_level'].isin(['low', 'medium'])
]

print(f"Low/Medium urgency calls: {len(low_med_urgency_df):,} ({len(low_med_urgency_df)/len(call_center_df)*100:.1f}%)")
print()

print("Top 20 Service Types (Low/Medium Urgency - Self-Service Candidates):")
for idx, (service, count) in enumerate(low_med_urgency_df['service_name'].value_counts().head(20).items(), 1):
    pct = count / len(call_center_df) * 100  # Percentage of total call center
    urgency_breakdown = low_med_urgency_df[low_med_urgency_df['service_name'] == service]['urgency_level'].value_counts()
    print(f"{idx:2d}. {service:40s} {count:6,} ({pct:5.1f}%)")
    for urg, urg_count in urgency_breakdown.items():
        print(f"     - {urg}: {urg_count:,}")
print()

# Identify neutral sentiment + routine service types
print("-" * 80)
print("ROUTINE SERVICES (Neutral Sentiment, Likely Informational)")
print("-" * 80)
print()

routine_df = call_center_df[
    (call_center_df['sentiment'] == 'neutral') &
    (call_center_df['urgency_level'].isin(['low', 'medium']))
]

print(f"Neutral sentiment + low/medium urgency: {len(routine_df):,} ({len(routine_df)/len(call_center_df)*100:.1f}%)")
print()

print("Top 15 Routine Service Types:")
for idx, (service, count) in enumerate(routine_df['service_name'].value_counts().head(15).items(), 1):
    pct = count / len(call_center_df) * 100
    print(f"{idx:2d}. {service:40s} {count:6,} ({pct:5.1f}%)")
print()

# Analyze description patterns for automation opportunities
print("-" * 80)
print("DESCRIPTION PATTERN ANALYSIS")
print("-" * 80)
print()

# Find services with empty/minimal descriptions (likely status checks or simple requests)
empty_desc_df = call_center_df[
    (call_center_df['description'].isna()) |
    (call_center_df['description'].str.strip() == '') |
    (call_center_df['description'].str.len() < 20)
]

print(f"Requests with empty/minimal descriptions: {len(empty_desc_df):,} ({len(empty_desc_df)/len(call_center_df)*100:.1f}%)")
print("\nTop 10 Service Types with Empty/Minimal Descriptions:")
for idx, (service, count) in enumerate(empty_desc_df['service_name'].value_counts().head(10).items(), 1):
    pct = count / len(empty_desc_df) * 100
    print(f"{idx:2d}. {service:40s} {count:5,} ({pct:5.1f}%)")
print()

# Find repeat service types by the same address (potential for proactive alerts)
print("-" * 80)
print("REPEAT CALLERS ANALYSIS (Same Address, Same Service Type)")
print("-" * 80)
print()

# Group by address and service name
repeat_calls = call_center_df.groupby(['address', 'service_name']).size().reset_index(name='call_count')
repeat_calls = repeat_calls[repeat_calls['call_count'] > 1].sort_values('call_count', ascending=False)

print(f"Addresses with repeat calls for same service: {len(repeat_calls):,}")
print(f"Total repeat calls: {repeat_calls['call_count'].sum():,}")
print()

print("Top 15 Repeat Service Patterns:")
for idx, row in repeat_calls.head(15).iterrows():
    if idx >= 15:
        break
    addr = row['address'][:40] if pd.notna(row['address']) else 'N/A'
    print(f"{idx+1:2d}. {addr:40s} | {row['service_name']:30s} | {row['call_count']} calls")
print()

# Top repeat service types
repeat_services = repeat_calls.groupby('service_name')['call_count'].sum().sort_values(ascending=False)
print("Top 10 Service Types with Repeat Calls:")
for idx, (service, count) in enumerate(repeat_services.head(10).items(), 1):
    addresses_affected = len(repeat_calls[repeat_calls['service_name'] == service])
    avg_repeats = count / addresses_affected
    print(f"{idx:2d}. {service:40s} {count:5,} repeat calls from {addresses_affected} addresses (avg {avg_repeats:.1f} per address)")
print()

# ============================================================================
# SUMMARY RECOMMENDATIONS
# ============================================================================
print("=" * 80)
print("SUMMARY: KEY RECOMMENDATIONS TO REDUCE CALL CENTER LOAD")
print("=" * 80)
print()

# Calculate potential impact
low_hanging_fruit = low_med_urgency_df[
    low_med_urgency_df['service_name'].isin(
        low_med_urgency_df['service_name'].value_counts().head(10).index
    )
]

routine_simple = routine_df[
    routine_df['service_name'].isin(
        routine_df['service_name'].value_counts().head(10).index
    )
]

print("RECOMMENDATION 1: Implement Self-Service for Top Low/Medium Urgency Services")
print(f"  - Potential call reduction: {len(low_hanging_fruit):,} calls ({len(low_hanging_fruit)/len(call_center_df)*100:.1f}%)")
print(f"  - Top services to prioritize:")
for idx, (service, count) in enumerate(low_med_urgency_df['service_name'].value_counts().head(5).items(), 1):
    print(f"    {idx}. {service}: {count:,} calls")
print()

print("RECOMMENDATION 2: Create FAQ/Knowledge Base for Routine Inquiries")
print(f"  - Potential call reduction: {len(routine_simple):,} calls ({len(routine_simple)/len(call_center_df)*100:.1f}%)")
print(f"  - Top services to document:")
for idx, (service, count) in enumerate(routine_df['service_name'].value_counts().head(5).items(), 1):
    print(f"    {idx}. {service}: {count:,} calls")
print()

print("RECOMMENDATION 3: Proactive Notifications for Repeat Callers")
print(f"  - Addresses with repeat calls: {len(repeat_calls):,}")
print(f"  - Total repeat calls: {repeat_calls['call_count'].sum():,}")
print(f"  - Top repeat services:")
for idx, (service, count) in enumerate(repeat_services.head(5).items(), 1):
    print(f"    {idx}. {service}: {count:,} repeat calls")
print()

print("RECOMMENDATION 4: Focus Call Center on High-Impact Issues")
print(f"  - High urgency + negative sentiment: {len(bottleneck_df):,} calls ({len(bottleneck_df)/len(call_center_df)*100:.1f}%)")
print(f"  - These are the issues that truly need human intervention")
print(f"  - Top agencies to support:")
for idx, (agency, count) in enumerate(bottleneck_df['agency_responsible'].value_counts().head(5).items(), 1):
    print(f"    {idx}. {agency}: {count:,} high-priority calls")
print()

# Calculate overall potential
total_potential_reduction = len(low_hanging_fruit) + len(routine_simple)
print("=" * 80)
print(f"TOTAL POTENTIAL CALL CENTER REDUCTION: {total_potential_reduction:,} calls ({total_potential_reduction/len(call_center_df)*100:.1f}%)")
print("=" * 80)
print()

print("Analysis complete!")
print()
