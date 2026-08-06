import urllib.request
import urllib.error
import time

import os

# Wait for the service to be available (useful right after deployment)
BASE_URL = os.environ.get("API_URL", "http://localhost:8000")
ENDPOINTS = [
    ("/today?units=imperial", "GET"),
    ("/today?units=metric", "GET"),
    ("/predict?units=imperial", "POST"),
    ("/predict?units=metric", "POST"),
]

def warm_cache():
    print(f"Warming up cache for {BASE_URL}...")
    
    # Simple retry loop to wait for the server to be ready
    for _ in range(30):
        try:
            req = urllib.request.Request(f"{BASE_URL}/health", method="GET")
            urllib.request.urlopen(req)
            break
        except Exception:
            time.sleep(1)
    else:
        print("Error: Could not reach the API after 30 seconds.")
        return

    for endpoint, method in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        print(f"Hitting {method} {url} ...", end=" ")
        try:
            # We pass empty data to force a POST request if method is POST
            data = b"" if method == "POST" else None
            req = urllib.request.Request(url, data=data, method=method)
            urllib.request.urlopen(req)
            print("OK!")
        except Exception as e:
            print(f"FAILED ({e})")

if __name__ == "__main__":
    warm_cache()
