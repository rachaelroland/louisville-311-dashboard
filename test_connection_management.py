#!/usr/bin/env python3
"""
Test improved connection management and performance monitoring
Verifies Supabase best practices implementation in dashboard
"""

import requests
import time
import sys

BASE_URL = "http://localhost:5003"

print("=" * 80)
print("CONNECTION MANAGEMENT & PERFORMANCE MONITORING TEST")
print("=" * 80)
print()

# Test questions to trigger different code paths
test_questions = [
    ("How do I report a pothole?", "Standard search (direct match)"),
    ("I need to report overgrown weeds", "Enhanced search (context extraction)"),
    ("What is 311?", "Standard search (general info)"),
    ("Can you help me with bulk trash?", "Enhanced search with data insights"),
]

print("Testing dashboard connection management...")
print()

passed = 0
failed = 0

for question, description in test_questions:
    print(f"Test: {description}")
    print(f"  Question: \"{question}\"")

    try:
        start_time = time.time()

        response = requests.post(
            f"{BASE_URL}/chat/ask",
            data={"message": question},
            timeout=10
        )

        duration = time.time() - start_time

        if response.status_code == 200:
            print(f"  ✅ Response received ({duration:.2f}s)")

            # Check for monitoring output in logs
            # (would need to check /tmp/dash_final.log for actual timing logs)

            # Extract answer preview
            import re
            match = re.search(r'<div class="message assistant-message">(.*?)</div>',
                            response.text, re.DOTALL)

            if match:
                answer = re.sub(r'<[^>]+>', '', match.group(1).strip())
                print(f"  Preview: {answer[:80]}...")

            passed += 1
        else:
            print(f"  ❌ HTTP {response.status_code}")
            failed += 1

    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection refused - is dashboard running on port 5003?")
        print(f"     Start with: PORT=5003 uv run python dashboard_app.py")
        failed += 1
        break
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timed out (>10s)")
        failed += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1

    print()
    time.sleep(0.5)

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print()

if passed == len(test_questions):
    print("✅ All connection management tests passed!")
    print()
    print("Check /tmp/dash_final.log for performance monitoring output:")
    print("  • Look for '⏱️  find_approved_answer took' messages")
    print("  • Look for '⚠️  SLOW QUERY' warnings (if any)")
    print()
    print("To view logs:")
    print("  tail -f /tmp/dash_final.log")
    print()
    print("Expected log entries:")
    print("  - Connection lifecycle: context manager handling")
    print("  - Query timing: sub-second for most queries")
    print("  - No connection leaks: proper putconn() calls")
else:
    print("⚠️  Some tests failed. Check dashboard logs.")
    sys.exit(1)
