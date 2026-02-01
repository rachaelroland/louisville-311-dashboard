#!/usr/bin/env python3
"""
Generate concise summary statistics for quick reference
"""

import pandas as pd
import json

# File paths
PROCESSED_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv"
RAW_CSV = "/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv"

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

print("=" * 80)
print("QUICK STATS: LOUISVILLE METRO 311 CALL CENTER 2024")
print("=" * 80)
print()

print("OVERALL METRICS")
print("-" * 80)
print(f"Total 311 Requests:              {len(merged_df):>10,}")
print(f"Call Center Requests:            {len(call_center_df):>10,}  ({len(call_center_df)/len(merged_df)*100:>5.1f}%)")
print()

print("URGENCY BREAKDOWN")
print("-" * 80)
urgency = call_center_df['urgency_level'].value_counts()
print(f"High Urgency:                    {urgency.get('high', 0):>10,}  ({urgency.get('high', 0)/len(call_center_df)*100:>5.1f}%)")
print(f"Medium Urgency:                  {urgency.get('medium', 0):>10,}  ({urgency.get('medium', 0)/len(call_center_df)*100:>5.1f}%)")
print(f"Low Urgency:                     {urgency.get('low', 0):>10,}  ({urgency.get('low', 0)/len(call_center_df)*100:>5.1f}%)")
print()

print("SENTIMENT BREAKDOWN")
print("-" * 80)
sentiment = call_center_df['sentiment'].value_counts()
print(f"Negative:                        {sentiment.get('negative', 0):>10,}  ({sentiment.get('negative', 0)/len(call_center_df)*100:>5.1f}%)")
print(f"Neutral:                         {sentiment.get('neutral', 0):>10,}  ({sentiment.get('neutral', 0)/len(call_center_df)*100:>5.1f}%)")
print(f"Positive:                        {sentiment.get('positive', 0):>10,}  ({sentiment.get('positive', 0)/len(call_center_df)*100:>5.1f}%)")
print()

# Calculate key segments
nsr_calls = call_center_df[call_center_df['service_name'].str.contains('NSR', na=False)]
low_med_urgency = call_center_df[call_center_df['urgency_level'].isin(['low', 'medium'])]
routine = call_center_df[(call_center_df['sentiment'] == 'neutral') & (call_center_df['urgency_level'].isin(['low', 'medium']))]
bottleneck = call_center_df[(call_center_df['urgency_level'] == 'high') & (call_center_df['sentiment'] == 'negative')]
empty_desc = call_center_df[(call_center_df['description'].isna()) | (call_center_df['description'].str.len() < 20)]

print("KEY OPPORTUNITY SEGMENTS")
print("-" * 80)
print(f"NSR (Info/Referral) Calls:       {len(nsr_calls):>10,}  ({len(nsr_calls)/len(call_center_df)*100:>5.1f}%)")
print(f"Low/Medium Urgency:              {len(low_med_urgency):>10,}  ({len(low_med_urgency)/len(call_center_df)*100:>5.1f}%)")
print(f"Routine (Neutral + Low/Med):     {len(routine):>10,}  ({len(routine)/len(call_center_df)*100:>5.1f}%)")
print(f"Empty/Minimal Description:       {len(empty_desc):>10,}  ({len(empty_desc)/len(call_center_df)*100:>5.1f}%)")
print(f"Bottleneck (High + Negative):    {len(bottleneck):>10,}  ({len(bottleneck)/len(call_center_df)*100:>5.1f}%)")
print()

print("SELF-SERVICE POTENTIAL")
print("-" * 80)
# Get top 10 low/med urgency services
top_selfservice = low_med_urgency['service_name'].value_counts().head(10)
total_selfservice = top_selfservice.sum()
print(f"Top 10 Self-Service Candidates:  {total_selfservice:>10,}  ({total_selfservice/len(call_center_df)*100:>5.1f}%)")
print()

for idx, (service, count) in enumerate(top_selfservice.items(), 1):
    print(f"  {idx:2d}. {service[:42]:42s} {count:>7,}")
print()

print("WASTE MANAGEMENT OPPORTUNITIES")
print("-" * 80)
waste_services = [
    'Solid Waste Container Request',
    'Solid Waste Missed Services',
    'Large Item Appointment',
    'Trash',
    'Solid Waste Violation'
]
waste_df = call_center_df[call_center_df['service_name'].isin(waste_services)]
print(f"Total Waste-Related Calls:       {len(waste_df):>10,}  ({len(waste_df)/len(call_center_df)*100:>5.1f}%)")
print()
for service in waste_services:
    count = len(call_center_df[call_center_df['service_name'] == service])
    if count > 0:
        print(f"  {service[:42]:42s} {count:>7,}")
print()

# Repeat callers
repeat_calls = call_center_df.groupby(['address', 'service_name']).size().reset_index(name='call_count')
repeat_calls = repeat_calls[repeat_calls['call_count'] > 1]
total_repeat = repeat_calls['call_count'].sum()

print("REPEAT CALLER IMPACT")
print("-" * 80)
print(f"Addresses with Repeat Calls:     {len(repeat_calls):>10,}")
print(f"Total Repeat Calls:              {total_repeat:>10,}  ({total_repeat/len(call_center_df)*100:>5.1f}%)")
print()

print("=" * 80)
print("RECOMMENDED ACTION PLAN")
print("=" * 80)
print()
print("1. IMMEDIATE (0-3 months)")
print("   - Implement FAQ for top 20 NSR topics")
print("   - Add waste collection schedule lookup on website")
print(f"   - Expected reduction: ~{len(nsr_calls)*.3:,.0f} calls (30% of NSR)")
print()
print("2. SHORT-TERM (3-6 months)")
print("   - Launch self-service portal for top 10 services")
print("   - Implement cart ordering/replacement online")
print(f"   - Expected reduction: ~{total_selfservice*.5:,.0f} calls (50% of top services)")
print()
print("3. MEDIUM-TERM (6-12 months)")
print("   - Proactive notifications for missed pickups")
print("   - Mobile app for service requests")
print(f"   - Expected reduction: ~{total_repeat*.6:,.0f} calls (60% of repeats)")
print()
print(f"TOTAL POTENTIAL REDUCTION: {len(nsr_calls)*.3 + total_selfservice*.5 + total_repeat*.6:,.0f} calls")
print(f"  ({(len(nsr_calls)*.3 + total_selfservice*.5 + total_repeat*.6)/len(call_center_df)*100:.1f}% of call center volume)")
print()
print("=" * 80)
