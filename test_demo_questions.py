#!/usr/bin/env python3
"""
Test realistic demo questions to verify system is ready
"""

import requests
import re
import time

# Realistic demo questions that residents would ask
demo_questions = [
    # Direct questions (should match approved answers)
    ("How do I report a pothole?", "Street Maintenance"),
    ("What is 311?", "General"),
    ("When is my trash pickup day?", "Waste Management"),
    ("How do I report a water main break?", "Water/Sewer"),
    ("How do I report a stray dog?", "Animal Control"),

    # Conversational questions (test flexibility)
    ("There's a big pothole on my street", "Should match pothole question"),
    ("My trash wasn't collected this morning", "Should match missed pickup"),
    ("I need to report overgrown weeds", "Should match code enforcement"),
    ("Can you help me with bulk trash?", "Should match bulk trash pickup"),
    ("Streetlight is out on my block", "Should match streetlight question"),

    # Complex/specific questions
    ("How do I report interior housing code violations?", "Code Enforcement - Safety"),
    ("There's a dangerous tree about to fall", "Should match tree question"),
    ("Traffic light is broken at intersection", "Should match traffic signal"),
    ("What's the difference between 311 and 911?", "General"),
    ("How long does it take to fix my issue?", "General"),
]

print("=" * 80)
print("DEMO READINESS TEST - Realistic 311 Questions")
print("=" * 80)
print()

results = {
    'matched': 0,
    'fallback': 0,
    'total': len(demo_questions)
}

for question, expected_category in demo_questions:
    print(f"Q: {question}")
    print(f"   Expected: {expected_category}")

    try:
        response = requests.post(
            "http://localhost:5003/chat/ask",
            data={"message": question},
            timeout=15
        )

        if response.status_code == 200:
            html = response.text

            # Extract assistant message
            match = re.search(r'<div class="message assistant-message">(.*?)</div>', html, re.DOTALL)

            if match:
                answer = match.group(1).strip()
                # Clean HTML tags
                answer = re.sub(r'<[^>]+>', '', answer)

                # Check for data insights
                has_insights = "📊" in answer or "⚠️" in answer

                # Check if answer looks like approved (starts with specific info vs "Great question!")
                looks_approved = not answer.startswith("Great question!") and not answer.startswith("I'm happy to help")

                if looks_approved:
                    results['matched'] += 1
                    status = "✅ APPROVED ANSWER"
                else:
                    results['fallback'] += 1
                    status = "⚠️  CLAUDE FALLBACK"

                if has_insights:
                    status += " + DATA INSIGHTS"

                print(f"   {status}")
                print(f"   Preview: {answer[:120]}...")
            else:
                print(f"   ❌ Could not extract response")
                results['fallback'] += 1
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results['fallback'] += 1

    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['fallback'] += 1

    print()
    time.sleep(0.5)  # Brief delay between requests

print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print(f"Total Questions:    {results['total']}")
print(f"Approved Answers:   {results['matched']} ({results['matched']/results['total']*100:.1f}%)")
print(f"Claude Fallback:    {results['fallback']} ({results['fallback']/results['total']*100:.1f}%)")
print()

if results['matched'] >= results['total'] * 0.8:
    print("✅ DEMO READY - 80%+ questions using approved answers")
elif results['matched'] >= results['total'] * 0.5:
    print("⚠️  NEEDS IMPROVEMENT - Only 50-80% using approved answers")
else:
    print("❌ NOT DEMO READY - Less than 50% using approved answers")

print("=" * 80)
