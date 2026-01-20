# Test script: test_timeout.py
import requests

print("Testing timeout...")
try:
    response = requests.get("https://wagslane.dev", timeout=5)
    print(f"Success! Status: {response.status_code}")
except requests.exceptions.Timeout:
    print("Timeout occurred!")
except Exception as e:
    print(f"Error: {e}")

