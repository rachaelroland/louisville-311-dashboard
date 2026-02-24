#!/usr/bin/env python3
"""
Test enhanced search with topic/entity extraction
"""

import requests
import re
import time

# Test questions that should benefit from enhanced search
test_questions = [
    ("How do I report a pothole on Main Street?", "Should extract location entity"),
    ("My neighbor has trash piling up in their yard", "Should identify waste/code enforcement topics"),
    ("There's a dangerous tree about to fall", "Should identify urgency and safety topic"),
    ("The traffic light at 4th and Broadway is broken", "Should extract location and identify street maintenance"),
    ("How do I report a stray dog?", "Should identify animal control category"),
]

print("=" * 80)
print("ENHANCED SEARCH TEST - Topic & Entity Extraction")
print("=" * 80)
print()

for question, expected in test_questions:
    print(f"Question: {question}")
    print(f"Expected: {expected}")

    try:
        response = requests.post(
            "http://localhost:5003/chat/ask",
            data={"message": question},
            timeout=15
        )

        if response.status_code == 200:
            # Extract assistant message
            html = response.text
            match = re.search(r'<div class="message assistant-message">(.*?)</div>', html, re.DOTALL)

            if match:
                answer = match.group(1).strip()
                # Clean HTML tags
                answer = re.sub(r'<[^>]+>', '', answer)

                # Check for data insights
                has_insights = "📊" in answer or "⚠️" in answer

                print(f"✅ Response received")
                if has_insights:
                    print(f"   💡 Includes data insights")
                print(f"   Preview: {answer[:150]}...")
            else:
                print(f"❌ Could not extract response")
        else:
            print(f"❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    time.sleep(1)  # Rate limiting

print("=" * 80)
print("Check /tmp/dashboard_enhanced.log for context extraction details")
print("Look for lines like: '📋 Extracted context: topics=...'")
print("=" * 80)
