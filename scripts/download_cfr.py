#!/usr/bin/env python3
"""Download CFR decompiler JAR."""
import os
import httpx

CFR_URL = "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"
TARGET = os.path.join(os.path.dirname(__file__), "..", "tools", "cfr.jar")

def main():
    target = os.path.abspath(TARGET)
    if os.path.isfile(target):
        print(f"CFR already exists at {target}")
        return

    os.makedirs(os.path.dirname(target), exist_ok=True)
    print(f"Downloading CFR from {CFR_URL}...")
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        response = client.get(CFR_URL)
        response.raise_for_status()
        with open(target, 'wb') as f:
            f.write(response.content)
    print(f"CFR downloaded to {target}")

if __name__ == "__main__":
    main()
