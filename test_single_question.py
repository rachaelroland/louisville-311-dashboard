#!/usr/bin/env python3
import requests
import re
import time

questions = [
    "I need to report overgrown weeds",
    "Can you help me with bulk trash?",
    "Streetlight is out on my block",
    "Traffic light is broken at intersection",
]

for q in questions:
    print(f"\nTesting: {q}")
    try:
        resp = requests.post("http://localhost:5003/chat/ask", data={"message": q}, timeout=15)
        if resp.status_code == 200:
            match = re.search(r'<div class="message assistant-message">(.*?)</div>', resp.text, re.DOTALL)
            if match:
                answer = re.sub(r'<[^>]+>', '', match.group(1).strip())
                print(f"Response: {answer[:100]}...")
        else:
            print(f"Error: HTTP {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)
