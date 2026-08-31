#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple regression test to verify locale precedence and persistence:
- URL parameter `?lang=` overrides session locale immediately
- Visiting with `?lang=` persists the selected language in session for subsequent requests
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def assert_equal(actual, expected, label):
    if actual == expected:
        print(f"✓ {label}: {actual}")
    else:
        print(f"✗ {label}: expected '{expected}', got '{actual}'")


def main():
    print("===== Testing Locale Precedence and Persistence =====")

    s = requests.Session()

    # 1) Set session explicitly to zh_CN
    print("\n-- Step 1: Switch session to zh_CN --")
    r = s.get(f"{BASE_URL}/switch_language/zh_CN", allow_redirects=True, timeout=10)
    print(f"Status: {r.status_code}")

    r = s.get(f"{BASE_URL}/debug_babel", timeout=10)
    data = r.json()
    assert_equal(data.get("current_locale"), "zh_CN", "Current locale after session switch")

    # 2) Visit with URL lang=en, should override session immediately
    print("\n-- Step 2: Visit with ?lang=en to override --")
    r = s.get(f"{BASE_URL}/debug_babel?lang=en", timeout=10)
    data = r.json()
    assert_equal(data.get("current_locale"), "en", "Current locale via URL override")

    # 3) Subsequent request without lang should persist 'en'
    print("\n-- Step 3: Subsequent request without lang should persist 'en' --")
    r = s.get(f"{BASE_URL}/debug_babel", timeout=10)
    data = r.json()
    assert_equal(data.get("current_locale"), "en", "Current locale persisted in session")

    # 4) Sanity check translations for a few keys
    print("\n-- Step 4: Verify a few translations under 'en' --")
    translations = data.get("translations") or {}
    print("Translations:")
    for k, v in translations.items():
        print(f"  '{k}' -> '{v}'")

    print("\n===== Test Completed =====")


if __name__ == "__main__":
    main()