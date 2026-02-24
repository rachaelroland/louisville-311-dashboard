#!/usr/bin/env python3
"""
Quick test to verify database integration is working
"""

import requests
import re

# Test questions that should match approved answers
test_questions = [
    "How do I report a pothole?",
    "What is 311?",
    "How do I submit a 311 service request?",
    "When is my trash pickup day?",
    "How do I report a water main break?",
]

print("=" * 80)
print("DATABASE INTEGRATION TEST")
print("=" * 80)
print()

for question in test_questions:
    print(f"Testing: {question}")

    try:
        response = requests.post(
            "http://localhost:5003/chat/ask",
            data={"message": question},
            timeout=15
        )

        if response.status_code == 200:
            # Extract assistant message from HTML
            html = response.text
            match = re.search(r'<div class="message assistant-message">(.*?)</div>', html, re.DOTALL)

            if match:
                answer = match.group(1).strip()
                # Clean HTML tags
                answer = re.sub(r'<[^>]+>', '', answer)
                answer = answer[:200] + "..." if len(answer) > 200 else answer

                print(f"✅ Response received")
                print(f"   Preview: {answer[:100]}...")
            else:
                print(f"❌ Could not extract response")
        else:
            print(f"❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()

print("=" * 80)
print("Test complete. Check dashboard logs for '✅ Using approved answer' messages")
print("=" * 80)
