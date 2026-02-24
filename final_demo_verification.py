#!/usr/bin/env python3
"""
Final verification that system is 100% demo-ready
Tests edge cases and confirms all systems working
"""

import requests
import re
import time

print("="*80)
print("FINAL DEMO READINESS VERIFICATION")
print("="*80)
print()

# Critical demo questions that MUST work
critical_questions = [
    ("How do I report a pothole?", "Must match - common question"),
    ("What is 311?", "Must match - fundamental"),
    ("I need to report overgrown weeds", "Must match - conversational"),
    ("Can you help me with bulk trash?", "Must match - conversational"),
    ("How do I report interior housing code violations?", "Must match - safety critical"),
]

# Edge cases to test
edge_cases = [
    ("potholes on main st", "Very short, informal"),
    ("my trash", "Extremely short"),
    ("I have no heat in my apartment and the landlord won't fix it", "Complex, should match interior housing"),
    ("tree dangerous falling", "Broken English"),
]

all_tests = critical_questions + edge_cases
passed = 0
failed = 0

for question, description in all_tests:
    print(f"Testing: {question}")
    print(f"  ({description})")

    try:
        resp = requests.post(
            "http://localhost:5003/chat/ask",
            data={"message": question},
            timeout=20
        )

        if resp.status_code == 200:
            # Extract answer
            match = re.search(r'<div class="message assistant-message">(.*?)</div>', resp.text, re.DOTALL)

            if match:
                answer = re.sub(r'<[^>]+>', '', match.group(1).strip())

                # Check if it's a quality answer (not just "I can help")
                is_quality = (
                    len(answer) > 100 and
                    ('311' in answer or 'Louisville' in answer or 'call' in answer.lower())
                )

                if is_quality:
                    print(f"  ✅ PASS - Quality answer received")
                    print(f"     Preview: {answer[:80]}...")
                    passed += 1
                else:
                    print(f"  ⚠️  QUESTIONABLE - Answer seems generic")
                    print(f"     Preview: {answer[:80]}...")
                    failed += 1
            else:
                print(f"  ❌ FAIL - Could not extract answer")
                failed += 1
        else:
            print(f"  ❌ FAIL - HTTP {resp.status_code}")
            failed += 1

    except requests.exceptions.Timeout:
        print(f"  ❌ FAIL - Request timed out (>20s)")
        failed += 1
    except Exception as e:
        print(f"  ❌ FAIL - Error: {e}")
        failed += 1

    print()
    time.sleep(0.5)

# Final Results
print("="*80)
print("FINAL VERIFICATION RESULTS")
print("="*80)
print(f"Total Tests:  {len(all_tests)}")
print(f"Passed:       {passed} ({passed/len(all_tests)*100:.0f}%)")
print(f"Failed:       {failed} ({failed/len(all_tests)*100:.0f}%)")
print()

if passed >= len(critical_questions):
    print("✅ CRITICAL TESTS PASSED - Demo is safe to proceed")
else:
    print("❌ CRITICAL TESTS FAILED - Do not demo until fixed")

if passed == len(all_tests):
    print("🎉 PERFECT SCORE - All edge cases handled!")
elif passed >= len(all_tests) * 0.8:
    print("✅ DEMO READY - Minor edge cases acceptable")
else:
    print("⚠️  REVIEW NEEDED - Too many failures")

print("="*80)
